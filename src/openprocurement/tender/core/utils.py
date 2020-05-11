# -*- coding: utf-8 -*-
import jmespath
from decimal import Decimal
from re import compile
from functools import wraps

from dateorro import (
    calc_datetime,
    calc_working_datetime,
    calc_normalized_datetime,
)
from dateorro.calculations import check_working_datetime
from iso8601 import parse_date
from jsonpointer import resolve_pointer
from functools import partial
from datetime import datetime, time, timedelta
from logging import getLogger
from time import sleep
from pyramid.exceptions import URLDecodeError
from pyramid.compat import decode_path_info
from pyramid.security import Allow
from cornice.resource import resource
from couchdb.http import ResourceConflict
from openprocurement.api.constants import (
    WORKING_DAYS,
    SANDBOX_MODE,
    TZ,
    WORKING_DATE_ALLOW_MIDNIGHT_FROM,
    NORMALIZED_CLARIFICATIONS_PERIOD_FROM,
    NORMALIZE_SHOULD_START_AFTER,
    RELEASE_2020_04_19,
    NORMALIZED_TENDER_PERIOD_FROM,
)
from openprocurement.api.utils import (
    get_now,
    context_unpack,
    get_revision_changes,
    apply_data_patch,
    update_logging_context,
    set_modetest_titles,
    error_handler,
    get_first_revision_date,
    handle_store_exceptions,
    append_revision,
)
from openprocurement.tender.core.constants import (
    BIDDER_TIME,
    SERVICE_TIME,
    AUCTION_STAND_STILL_TIME,
    NORMALIZED_COMPLAINT_PERIOD_FROM,
    ALP_MILESTONE_REASONS,
)
from openprocurement.tender.core.traversal import factory
from openprocurement.tender.openua.constants import AUCTION_PERIOD_TIME
from jsonpointer import JsonPointerException
from jsonpatch import JsonPatchException, apply_patch as apply_json_patch
from barbecue import chef
import math

LOGGER = getLogger("openprocurement.tender.core")

ACCELERATOR_RE = compile(r".accelerator=(?P<accelerator>\d+)")


optendersresource = partial(resource, error_handler=error_handler, factory=factory)


def normalize_should_start_after(start_after, tender):
    if SANDBOX_MODE and tender.submissionMethodDetails and u"quick" in tender.submissionMethodDetails:
        return start_after
    date = tender.enquiryPeriod and tender.enquiryPeriod.startDate or get_now()
    if NORMALIZE_SHOULD_START_AFTER < date:
        return calc_normalized_datetime(start_after, ceil=True)
    return start_after


def calc_auction_end_time(bids, start):
    return start + bids * BIDDER_TIME + SERVICE_TIME + AUCTION_STAND_STILL_TIME


def generate_tender_id(ctime, db, server_id=""):
    key = ctime.date().isoformat()
    tenderIDdoc = "tenderID_" + server_id if server_id else "tenderID"
    while True:
        try:
            tenderID = db.get(tenderIDdoc, {"_id": tenderIDdoc})
            index = tenderID.get(key, 1)
            tenderID[key] = index + 1
            db.save(tenderID)
        except ResourceConflict:  # pragma: no cover
            pass
        except Exception:  # pragma: no cover
            sleep(1)
        else:
            break
    return "UA-{:04}-{:02}-{:02}-{:06}{}".format(
        ctime.year, ctime.month, ctime.day, index, server_id and "-" + server_id
    )


def tender_serialize(request, tender_data, fields):
    tender = request.tender_from_data(tender_data, raise_error=False)
    if tender is None:
        return dict([(i, tender_data.get(i, "")) for i in ["procurementMethodType", "dateModified", "id"]])
    tender.__parent__ = request.context
    return dict([(i, j) for i, j in tender.serialize(tender.status).items() if i in fields])


def save_tender(request):
    tender = request.validated["tender"]

    if tender.mode == u"test":
        set_modetest_titles(tender)

    patch = get_revision_changes(tender.serialize("plain"), request.validated["tender_src"])
    if patch:
        now = get_now()
        append_tender_revision(request, tender, patch, now)

        old_date_modified = tender.dateModified
        if getattr(tender, "modified", True):
            tender.dateModified = now

        with handle_store_exceptions(request):
            tender.store(request.registry.db)
            LOGGER.info(
                "Saved tender {}: dateModified {} -> {}".format(
                    tender.id,
                    old_date_modified and old_date_modified.isoformat(),
                    tender.dateModified.isoformat()
                ),
                extra=context_unpack(request, {"MESSAGE_ID": "save_tender"}, {"RESULT": tender.rev}),
            )
            return True


def append_tender_revision(request, tender, patch, date):
    status_changes = [p for p in patch if all([
        not p["path"].startswith("/bids/"),
        p["path"].endswith("/status"),
        p["op"] == "replace"
    ])]
    for change in status_changes:
        obj = resolve_pointer(tender, change["path"].replace("/status", ""))
        if obj and hasattr(obj, "date"):
            date_path = change["path"].replace("/status", "/date")
            if obj.date and not any([p for p in patch if date_path == p["path"]]):
                patch.append({"op": "replace", "path": date_path, "value": obj.date.isoformat()})
            elif not obj.date:
                patch.append({"op": "remove", "path": date_path})
            obj.date = date
    return append_revision(request, tender, patch)


def apply_patch(request, data=None, save=True, src=None):
    data = request.validated["data"] if data is None else data
    patch = data and apply_data_patch(src or request.context.serialize(), data)
    if patch:
        request.context.import_data(patch)
        if save:
            return save_tender(request)


def remove_draft_bids(request):
    tender = request.validated["tender"]
    if [bid for bid in tender.bids if getattr(bid, "status", "active") == "draft"]:
        LOGGER.info("Remove draft bids", extra=context_unpack(request, {"MESSAGE_ID": "remove_draft_bids"}))
        tender.bids = [bid for bid in tender.bids if getattr(bid, "status", "active") != "draft"]


def cleanup_bids_for_cancelled_lots(tender):
    cancelled_lots = [i.id for i in tender.lots if i.status == "cancelled"]
    if cancelled_lots:
        return
    cancelled_items = [i.id for i in tender.items if i.relatedLot in cancelled_lots]
    cancelled_features = [
        i.code
        for i in (tender.features or [])
        if i.featureOf == "lot"
        and i.relatedItem in cancelled_lots
        or i.featureOf == "item"
        and i.relatedItem in cancelled_items
    ]
    for bid in tender.bids:
        bid.documents = [i for i in bid.documents if i.documentOf != "lot" or i.relatedItem not in cancelled_lots]
        bid.parameters = [i for i in bid.parameters if i.code not in cancelled_features]
        bid.lotValues = [i for i in bid.lotValues if i.relatedLot not in cancelled_lots]
        if not bid.lotValues:
            tender.bids.remove(bid)


def has_unanswered_questions(tender, filter_cancelled_lots=True):
    if filter_cancelled_lots and tender.lots:
        active_lots = [l.id for l in tender.lots if l.status == "active"]
        active_items = [i.id for i in tender.items if not i.relatedLot or i.relatedLot in active_lots]
        return any(
            [
                not i.answer
                for i in tender.questions
                if i.questionOf == "tender"
                or i.questionOf == "lot"
                and i.relatedItem in active_lots
                or i.questionOf == "item"
                and i.relatedItem in active_items
            ]
        )
    return any([not i.answer for i in tender.questions])


def has_unanswered_complaints(tender, filter_cancelled_lots=True):
    if filter_cancelled_lots and tender.lots:
        active_lots = [l.id for l in tender.lots if l.status == "active"]
        return any(
            [
                i.status in tender.block_tender_complaint_status
                for i in tender.complaints
                if not i.relatedLot or (i.relatedLot and i.relatedLot in active_lots)
            ]
        )
    return any([i.status in tender.block_tender_complaint_status for i in tender.complaints])


def extract_tender_adapter(request, tender_id):
    db = request.registry.db
    doc = db.get(tender_id)
    if doc is not None and doc.get("doc_type") == "tender":
        request.errors.add("url", "tender_id", "Archived")
        request.errors.status = 410
        raise error_handler(request.errors)
    elif doc is None or doc.get("doc_type") != "Tender":
        request.errors.add("url", "tender_id", "Not Found")
        request.errors.status = 404
        raise error_handler(request.errors)

    return request.tender_from_data(doc)


def extract_tender(request):
    try:
        # empty if mounted under a path in mod_wsgi, for example
        path = decode_path_info(request.environ["PATH_INFO"] or "/")
    except KeyError:
        path = "/"
    except UnicodeDecodeError as e:
        raise URLDecodeError(e.encoding, e.object, e.start, e.end, e.reason)

    tender_id = ""
    # extract tender id
    parts = path.split("/")
    if len(parts) < 4 or parts[3] != "tenders":
        return

    tender_id = parts[4]
    return extract_tender_adapter(request, tender_id)


class isTender(object):
    """ Route predicate. """

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return "procurementMethodType = %s" % (self.val,)

    phash = text

    def __call__(self, context, request):
        if request.tender is not None:
            return getattr(request.tender, "procurementMethodType", None) == self.val
        return False


class SubscribersPicker(isTender):
    """ Subscriber predicate. """

    def __call__(self, event):
        if event.tender is not None:
            return getattr(event.tender, "procurementMethodType", None) == self.val
        return False


def register_tender_procurementMethodType(config, model):
    """Register a tender procurementMethodType.
    :param config:
        The pyramid configuration object that will be populated.
    :param model:
        The tender model class
    """
    config.registry.tender_procurementMethodTypes[model.procurementMethodType.default] = model


def tender_from_data(request, data, raise_error=True, create=True):
    procurementMethodType = data.get("procurementMethodType", "belowThreshold")
    model = request.registry.tender_procurementMethodTypes.get(procurementMethodType)
    if model is None and raise_error:
        request.errors.add("data", "procurementMethodType", "Not implemented")
        request.errors.status = 415
        raise error_handler(request.errors)
    update_logging_context(request, {"tender_type": procurementMethodType})
    if model is not None and create:
        if request.environ.get("REQUEST_METHOD") == "GET" and data.get("revisions"):
            # to optimize get requests to tenders with many revisions
            copy_data = dict(**data)  # changing of the initial dict is a bad practice
            copy_data["revisions"] = data["revisions"][:1]  # leave first revision for validations
            model = model(copy_data)
        else:
            model = model(data)
    return model


def get_tender_accelerator(context):
    if context and "procurementMethodDetails" in context and context["procurementMethodDetails"]:
        re_obj = ACCELERATOR_RE.search(context["procurementMethodDetails"])
        if re_obj and "accelerator" in re_obj.groupdict():
            return int(re_obj.groupdict()["accelerator"])
    return None


def acceleratable(wrapped):
    @wraps(wrapped)
    def wrapper(date_obj, timedelta_obj, tender=None, working_days=False, calendar=WORKING_DAYS):
        accelerator = get_tender_accelerator(tender)
        if accelerator:
            return calc_datetime(date_obj, timedelta_obj, accelerator=accelerator)
        return wrapped(date_obj, timedelta_obj, tender=tender, working_days=working_days, calendar=calendar)
    return wrapper


@acceleratable
def calculate_tender_date(date_obj, timedelta_obj, tender=None, working_days=False, calendar=WORKING_DAYS):
    if working_days:
        tender_date = get_first_revision_date(tender, default=get_now())
        midnight = tender_date > WORKING_DATE_ALLOW_MIDNIGHT_FROM
        return calc_working_datetime(date_obj, timedelta_obj, midnight, calendar)
    else:
        return calc_datetime(date_obj, timedelta_obj)


def calculate_period_start_date(date_obj, timedelta_obj, normalized_from_date_obj, tender=None):
    tender_date = get_first_revision_date(tender, default=get_now())
    if tender_date > normalized_from_date_obj:
        return calc_normalized_datetime(date_obj, ceil=timedelta_obj > timedelta())
    else:
        return date_obj


@acceleratable
def calculate_tender_business_date(date_obj, timedelta_obj, tender=None, working_days=False, calendar=WORKING_DAYS):
    start_obj = calculate_period_start_date(date_obj, timedelta_obj, NORMALIZED_TENDER_PERIOD_FROM, tender)
    return calculate_tender_date(start_obj, timedelta_obj, tender, working_days, calendar)


@acceleratable
def calculate_complaint_business_date(date_obj, timedelta_obj, tender=None, working_days=False, calendar=WORKING_DAYS):
    start_obj = calculate_period_start_date(date_obj, timedelta_obj, NORMALIZED_COMPLAINT_PERIOD_FROM, tender)
    return calculate_tender_date(start_obj, timedelta_obj, tender, working_days, calendar)


@acceleratable
def calculate_clarif_business_date(date_obj, timedelta_obj, tender=None, working_days=False, calendar=WORKING_DAYS):
    start_obj = calculate_period_start_date(date_obj, timedelta_obj, NORMALIZED_CLARIFICATIONS_PERIOD_FROM, tender)
    return calculate_tender_date(start_obj, timedelta_obj, tender, working_days, calendar)


def calculate_date_diff(dt1, dt2, working_days=True, calendar=WORKING_DAYS):
    if not working_days:
        return dt1 - dt2

    date2 = dt2

    days = 0
    while dt1.date() > date2.date():
        date2 += timedelta(days=1)
        if check_working_datetime(date2, calendar=calendar):
            days += 1

    diff = dt1 - date2

    return timedelta(days) + diff


def requested_fields_changes(request, fieldnames):
    changed_fields = request.validated["json_data"].keys()
    return set(fieldnames) & set(changed_fields)


def convert_to_decimal(value):
    """
    Convert other to Decimal.
    """
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, long)):
        return Decimal(value)
    if isinstance(value, (float)):
        return Decimal(repr(value))

    raise TypeError("Unable to convert %s to Decimal" % value)


def check_auction_period(period, tender):
    if period and period.startDate and period.shouldStartAfter:
        start = parse_date(period.shouldStartAfter)
        date = calculate_tender_date(start, AUCTION_PERIOD_TIME, tender, True)
        return period.startDate > date
    return False


def restrict_value_to_bounds(value, min_value, max_value):
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def round_up_to_ten(value):
    return int(math.ceil(value / 10.) * 10)


def calculate_total_complaints(tender):
    total_complaints = sum([len(i.get("complaints", [])) for i in tender.cancellations])

    if hasattr(tender, "awards"):
        total_complaints += sum([len(i.complaints) for i in tender.awards])

    if hasattr(tender, "complaints"):
        total_complaints += len(tender.complaints)

    if hasattr(tender, "qualifications"):
        total_complaints += sum([len(i.complaints) for i in tender.qualifications])

    return total_complaints


def check_skip_award_complaint_period(tender):
    return (
        tender.procurementMethodType == "belowThreshold"
        and tender.get("procurementMethodRationale", "") == "simple"
    )


class CancelTenderLot(object):

    def __call__(self, request, cancellation):
        if cancellation.status == "active":
            from openprocurement.tender.core.validation import validate_absence_of_pending_accepted_satisfied_complaints
            validate_absence_of_pending_accepted_satisfied_complaints(request, cancellation)
            if cancellation.relatedLot:
                self.cancel_lot(request, cancellation)
            else:
                self.cancel_tender(request)

    @staticmethod
    def add_next_award_method(request):
        raise NotImplementedError

    def cancel_tender(self, request):
        tender = request.validated["tender"]
        if tender.status in ["active.tendering", "active.auction"]:
            tender.bids = []
        tender.status = "cancelled"

    def cancel_lot(self, request, cancellation):
        tender = request.validated["tender"]
        self._cancel_lots(tender, cancellation)
        self._lot_update_check_tender_status(request, tender)

        if tender.status == "active.auction" and all(
                i.auctionPeriod and i.auctionPeriod.endDate
                for i in tender.lots
                if i.numberOfBids > 1 and i.status == "active"
        ):
            self.add_next_award_method(request)

    def _lot_update_check_tender_status(self, request, tender):
        lot_statuses = {lot.status for lot in tender.lots}
        if lot_statuses == {"cancelled"}:
            self.cancel_tender(request)
        elif not lot_statuses.difference({"unsuccessful", "cancelled"}):
            tender.status = "unsuccessful"
        elif not lot_statuses.difference({"complete", "unsuccessful", "cancelled"}):
            tender.status = "complete"

    @staticmethod
    def _cancel_lots(tender, cancellation):
        for lot in tender.lots:
            if lot.id == cancellation.relatedLot:
                lot.status = "cancelled"


def check_cancellation_status(request, cancel_class=CancelTenderLot):

    tender = request.validated["tender"]
    cancellations = tender.cancellations
    complaint_statuses = ["invalid", "declined", "stopped", "mistaken", "draft"]

    cancel_tender_lot = cancel_class()

    for cancellation in cancellations:
        complaint_period = cancellation.complaintPeriod
        if (
            cancellation.status == "pending"
            and complaint_period
            and complaint_period.endDate.astimezone(TZ) <= get_now()
            and all([i.status in complaint_statuses for i in cancellation.complaints])
        ):
            cancellation.status = "active"
            cancel_tender_lot(request, cancellation)


def block_tender(request):
    tender = request.validated["tender"]
    new_rules = get_first_revision_date(tender, default=get_now()) > RELEASE_2020_04_19

    if not new_rules:
        return False

    if any(i.status == "pending" for i in tender.cancellations):
        return True

    accept_tender = all(
        any(j.status == "resolved" for j in i.complaints)
        for i in tender.cancellations
        if i.status == "unsuccessful" and getattr(i, "complaints", None)
    )

    return not accept_tender


def extend_next_check_by_complaint_period_ends(tender, checks):
    """
    should be added to next_check tender methods
    to schedule switching complaints draft-mistaken and others
    """
    # no need to check procedures that don't have cancellation complaints
    excluded = ("belowThreshold", "closeFrameworkAgreementSelectionUA")
    for cancellation in tender.cancellations:
        if cancellation.status == "pending":
            # adding check
            complaint_period = getattr(cancellation, "complaintPeriod", None)
            if complaint_period and complaint_period.endDate and tender.procurementMethodType not in excluded:
                # this check can switch complaint statuses to mistaken + switch cancellation to active
                checks.append(cancellation.complaintPeriod.endDate.astimezone(TZ))

    # all the checks below only supposed to trigger complaint draft->mistaken switches
    # if any object contains a draft complaint, it's complaint end period is added to the checks
    # periods can be in the past, then the check expected to run once and immediately fix the complaint
    def has_draft_complaints(item):
        return any(c.status == "draft" and c.type == "complaint" for c in item.complaints)

    complaint_period = getattr(tender, "complaintPeriod", None)
    if complaint_period and complaint_period.endDate and has_draft_complaints(tender):
        checks.append(complaint_period.endDate.astimezone(TZ))

    qualification_period = getattr(tender, "qualificationPeriod", None)
    if qualification_period and qualification_period.endDate \
       and any(has_draft_complaints(q) for q in tender.qualifications):
        checks.append(tender.qualificationPeriod.endDate.astimezone(TZ))

    for award in tender.awards:
        complaint_period = getattr(award, "complaintPeriod", None)
        if complaint_period and complaint_period.endDate and has_draft_complaints(award):
            checks.append(award.complaintPeriod.endDate.astimezone(TZ))


def check_complaint_statuses_at_complaint_period_end(tender, now):
    """
    this one probably should run before "check_cancellation_status" (that switch pending cancellation to active)
    so that draft complaints will remain the status
    also cancellation complaint changes will be able to affect statuses of cancellations
    """
    if get_first_revision_date(tender, default=now) < RELEASE_2020_04_19:
        return
    # only for tenders from RELEASE_2020_04_19

    def check_complaints(complaints):
        for complaint in complaints:
            if complaint.status == "draft" and complaint.type == "complaint":
                complaint.status = "mistaken"
                complaint.rejectReason = "complaintPeriodEnded"

    # cancellation complaints
    for cancellation in tender.cancellations:
        complaint_period = getattr(cancellation, "complaintPeriod", None)
        if complaint_period and complaint_period.endDate and cancellation.complaintPeriod.endDate < now:
            check_complaints(cancellation.complaints)

    # tender complaints
    complaint_period = getattr(tender, "complaintPeriod", None)
    if complaint_period and complaint_period.endDate and complaint_period.endDate < now:
        check_complaints(tender.complaints)

    # tender qualification complaints
    qualification_period = getattr(tender, "qualificationPeriod", None)
    if qualification_period and qualification_period.endDate and qualification_period.endDate < now:
        for qualification in tender.qualifications:
            check_complaints(qualification.complaints)

    # tender award complaints
    for award in tender.awards:
        complaint_period = getattr(award, "complaintPeriod", None)
        if complaint_period and complaint_period.endDate and complaint_period.endDate < now:
            check_complaints(award.complaints)


def get_contract_supplier_permissions(contract):
    """
    Set `upload_contract_document` permissions for award in `active` status owners
    """
    suppliers_permissions = []
    if not hasattr(contract, "__parent__") or 'bids' not in contract.__parent__:
        return suppliers_permissions
    win_bid_id = jmespath.search("awards[?id=='{}'].bid_id".format(contract.awardID), contract.__parent__._data)[0]
    win_bid = jmespath.search("bids[?id=='{}'].[owner,owner_token]".format(win_bid_id), contract.__parent__._data)[0]
    bid_acl = "_".join(win_bid)
    suppliers_permissions.extend([(Allow, bid_acl, "upload_contract_documents"), (Allow, bid_acl, "edit_contract")])
    return suppliers_permissions


def get_contract_supplier_roles(contract):
    roles = {}
    if 'bids' not in contract.__parent__:
        return roles
    bid_id = jmespath.search("awards[?id=='{}'].bid_id".format(contract.awardID), contract.__parent__)[0]
    bid_data = jmespath.search("bids[?id=='{}'].[owner,owner_token]".format(bid_id), contract.__parent__)[0]
    roles['_'.join(bid_data)] = 'contract_supplier'
    return roles


def prepare_bids_for_awarding(tender, bids, lot_id=None):
    """
    Used by add_next_award method
    :param tender:
    :param bids
    :param lot_id:
    :return: list of bid dict objects sorted in a way they will be selected as winners
    """
    lot_items = [i.id for i in tender.items if i.relatedLot == lot_id]  # all items in case of non-lot tender
    features = [
         i for i in (tender.features or [])
         if i.featureOf == "tenderer"
         or i.featureOf == "lot" and i.relatedItem == lot_id
         or i.featureOf == "item" and i.relatedItem in lot_items
    ]  # all features in case of non-lot tender
    codes = [i.code for i in features]
    active_bids = []
    for bid in bids:
        if bid.status == "active":
            bid_params = [i for i in bid.parameters if i.code in codes]
            if lot_id:
                for lot_value in bid.lotValues:
                    if lot_value.relatedLot == lot_id and getattr(lot_value, "status", "active") == "active":
                        active_bids.append(
                            {
                                "id": bid.id,
                                "value": lot_value.value.serialize(),
                                "tenderers": bid.tenderers,
                                "parameters": bid_params,
                                "date": lot_value.date,
                            }
                        )
                        continue  # only one lotValue in a bid is expected
            else:
                active_bids.append(
                    {
                        "id": bid.id,
                        "value": bid.value.serialize(),
                        "tenderers": bid.tenderers,
                        "parameters": bid_params,
                        "date": bid.date,
                    }
                )
    configurator = tender.__parent__.request.content_configurator
    bids = chef(
        active_bids, features,
        ignore="",  # filters by id, shouldn't be a part of this lib
        reverse=configurator.reverse_awarding_criteria,
        awarding_criteria_key=configurator.awarding_criteria_key,
    )
    return bids


def exclude_unsuccessful_awarded_bids(tender, bids, lot_id):
    lot_awards = [i for i in tender.awards if i.lotID == lot_id]  # all awards in case of non-lot tender
    ignore_bid_ids = [b.bid_id for b in lot_awards if b.status == "unsuccessful"]
    bids = filter(lambda b: b["id"] not in ignore_bid_ids, bids)
    return bids


# low price milestones
def prepare_award_milestones(tender, bid, all_bids, lot_id=None):
    """
    :param tender:
    :param bid: a bid to check
    :param all_bids: prepared the way that "value" key exists even for multi-lot
    :param lot_id:
    :return:
    """
    milestones = []
    if (
        getattr(tender, "procurementMethodType", "") in ("esco", "aboveThresholdUA.defense")
        or get_first_revision_date(tender, default=get_now()) < RELEASE_2020_04_19
    ):
        return milestones   # skipping

    def ratio_of_two_values(v1, v2):
        return 1 - Decimal(v1) / Decimal(v2)

    if len(all_bids) > 1:
        reasons = []
        amount = bid["value"]["amount"]
        #  1st criteria
        mean_value = get_mean_value_tendering_bids(
            tender, all_bids, lot_id=lot_id, exclude_bid_id=bid["id"],
        )
        if ratio_of_two_values(amount, mean_value) >= Decimal("0.4"):
            reasons.append(ALP_MILESTONE_REASONS[0])

        # 2nd criteria
        for n, b in enumerate(all_bids):
            if b["id"] == bid["id"]:
                index = n
                break
        else:
            raise AssertionError("Selected bid not in the full list")  # should never happen
        following_index = index + 1
        if following_index < len(all_bids):  # selected bid has the following one
            following_bid = all_bids[following_index]
            following_amount = following_bid["value"]["amount"]
            if ratio_of_two_values(amount, following_amount) >= Decimal("0.3"):
                reasons.append(ALP_MILESTONE_REASONS[1])
        if reasons:
            milestones.append(
                {
                    "code": "alp",
                    "description": u" / ".join(reasons)
                }
            )
    return milestones


def get_mean_value_tendering_bids(tender, bids, lot_id, exclude_bid_id):
    before_auction_bids = get_bids_before_auction_results(tender)
    before_auction_bids = prepare_bids_for_awarding(
        tender, before_auction_bids, lot_id=lot_id,
    )
    initial_amounts = {
        b["id"]: float(b["value"]["amount"])
        for b in before_auction_bids
    }
    initial_values = [
        initial_amounts[b["id"]]
        for b in bids
        if b["id"] != exclude_bid_id  # except the bid being checked
    ]
    mean_value = sum(initial_values) / float(len(initial_values))
    return mean_value


def get_bids_before_auction_results(tender):
    request = tender.__parent__.request
    if tender.status == "active.auction":  # this request is posting auction results
        initial_doc = request.validated["tender_src"]
    else:  # after auction results posted
        initial_doc = tender.serialize()
        auction_revisions = [revision for revision in reversed(list(tender.revisions))
                             if revision["author"] == "auction"]
        if not auction_revisions:
            LOGGER.exception(
                "Can't find auction revisions, tendering bid amounts will be taken as they are",
                extra=context_unpack(request, {"MESSAGE_ID": "fail_get_auction_revisions"})
            )
        for revision in auction_revisions:
            try:
                initial_doc = apply_json_patch(initial_doc, revision["changes"])
            except (JsonPointerException, JsonPatchException) as e:
                LOGGER.exception(e, extra=context_unpack(request, {"MESSAGE_ID": "fail_get_tendering_bids"}))

    bid_model = type(tender).bids.model_class

    initial_bids_list = []
    for b in initial_doc["bids"]:
        m = bid_model(b)
        m.__parent__ = tender
        initial_bids_list.append(m)

    return initial_bids_list


def flatten_multidimensional_list(list_to_flatten):
    for element in list_to_flatten:
        if isinstance(element,(list, tuple)):
            for x in flatten_multidimensional_list(element):
                yield x
        else:
            yield element


def get_all_nested_from_the_object(objects_to_find, obj):
    nested_regex = ["", "*.", "*[*]."]
    search_query = ' || '.join([item + objects_to_find for item in nested_regex])
    nested_objects = jmespath.search(search_query, obj)
    nested_objects = list(flatten_multidimensional_list(nested_objects))
    return nested_objects
