# -*- coding: utf-8 -*-
import jmespath
from decimal import Decimal
from re import compile

from dateorro import (
    calc_datetime,
    calc_working_datetime,
    calc_normalized_datetime,
)
from dateorro.calculations import check_working_datetime
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
    RELEASE_2020_04_19,
)
from openprocurement.api.utils import error_handler, get_first_revision_date, handle_store_exceptions, append_revision
from openprocurement.api.utils import (
    get_now,
    context_unpack,
    get_revision_changes,
    apply_data_patch,
    update_logging_context,
    set_modetest_titles,
)
from openprocurement.tender.core.constants import (
    BIDDER_TIME,
    SERVICE_TIME,
    AUCTION_STAND_STILL_TIME,
    NORMALIZED_COMPLAINT_PERIOD_FROM,
)
from openprocurement.tender.core.traversal import factory
import math

LOGGER = getLogger("openprocurement.tender.core")

ACCELERATOR_RE = compile(r".accelerator=(?P<accelerator>\d+)")


optendersresource = partial(resource, error_handler=error_handler, factory=factory)


def rounding_shouldStartAfter(start_after, tender, use_from=datetime(2016, 7, 16, tzinfo=TZ)):
    if use_from < (tender.enquiryPeriod and tender.enquiryPeriod.startDate or get_now()) and not (
        SANDBOX_MODE and tender.submissionMethodDetails and u"quick" in tender.submissionMethodDetails
    ):
        midnigth = datetime.combine(start_after.date(), time(0, tzinfo=start_after.tzinfo))
        if start_after > midnigth:
            start_after = midnigth + timedelta(1)
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


def calculate_tender_date(date_obj, timedelta_obj, tender, working_days, calendar=WORKING_DAYS):
    tender_date = get_first_revision_date(tender, default=get_now())
    if working_days:
        midnight = tender_date > WORKING_DATE_ALLOW_MIDNIGHT_FROM
        return calc_working_datetime(date_obj, timedelta_obj, midnight, calendar)
    else:
        return calc_datetime(date_obj, timedelta_obj)


def calculate_tender_business_date(date_obj, timedelta_obj, tender=None, working_days=False, calendar=WORKING_DAYS):
    accelerator = get_tender_accelerator(tender)
    if accelerator:
        return calc_datetime(date_obj, timedelta_obj, accelerator)
    return calculate_tender_date(date_obj, timedelta_obj, tender, working_days, calendar)


def calculate_complaint_business_date(date_obj, timedelta_obj, tender=None, working_days=False, calendar=WORKING_DAYS):
    accelerator = get_tender_accelerator(tender)
    if accelerator:
        return calc_datetime(date_obj, timedelta_obj, accelerator)
    tender_date = get_first_revision_date(tender, default=get_now())
    if tender_date > NORMALIZED_COMPLAINT_PERIOD_FROM:
        source_date_obj = calc_normalized_datetime(date_obj, ceil=timedelta_obj > timedelta())
    else:
        source_date_obj = date_obj
    return calculate_tender_date(source_date_obj, timedelta_obj, tender, working_days, calendar)


def calculate_clarifications_business_date(date_obj, timedelta_obj, tender=None, working_days=False, calendar=WORKING_DAYS):
    accelerator = get_tender_accelerator(tender)
    if accelerator:
        return calc_datetime(date_obj, timedelta_obj, accelerator)
    tender_date = get_first_revision_date(tender, default=get_now())
    if tender_date > NORMALIZED_CLARIFICATIONS_PERIOD_FROM:
        source_date_obj = calc_normalized_datetime(date_obj, ceil=timedelta_obj > timedelta())
    else:
        source_date_obj = date_obj
    return calculate_tender_date(source_date_obj, timedelta_obj, tender, working_days, calendar)


def calculate_date_diff(dt1, dt2, working_days=True, calendar=WORKING_DAYS):
    if not working_days:
        return dt1 - dt2

    date2 = dt2

    days = 0
    while dt1 > date2:
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


def restrict_value_to_bounds(value, min_value, max_value):
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def round_up_to_ten(value):
    return int(math.ceil(value / 10.) * 10)


def calculate_total_complaints(tender):
    total_complaints = sum([len(i.complaints) for i in tender.cancellations])

    if hasattr(tender, "awards"):
        total_complaints += sum([len(i.complaints) for i in tender.awards])
    if hasattr(tender, "complaints"):
        total_complaints += len(tender.complaints)

    if hasattr(tender, "qualifications"):
        total_complaints = sum(
            [len(i.complaints) for i in tender.qualifications],
            total_complaints
        )

    return total_complaints


from openprocurement.tender.core.validation import validate_absence_of_pending_accepted_satisfied_complaints


class CancelTenderLot(object):

    def __call__(self, request, cancellation):
        if cancellation.status == "active":
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
