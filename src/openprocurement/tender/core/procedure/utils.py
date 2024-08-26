import math
from copy import deepcopy
from datetime import datetime
from hashlib import sha512
from logging import getLogger
from typing import Optional
from uuid import uuid4

from barbecue import vnmax
from dateorro import calc_normalized_datetime
from jsonpatch import JsonPatchException
from jsonpatch import apply_patch as apply_json_patch
from jsonpointer import JsonPointerException, resolve_pointer
from pyramid.compat import decode_path_info
from pyramid.exceptions import URLDecodeError
from schematics.exceptions import ValidationError

from openprocurement.api.constants import RELEASE_2020_04_19, TZ
from openprocurement.api.context import get_json_data, get_now
from openprocurement.api.mask import mask_object_data
from openprocurement.api.mask_deprecated import mask_object_data_deprecated
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.utils import (
    append_revision,
    apply_data_patch,
    get_revision_changes,
    parse_date,
)
from openprocurement.api.utils import (
    context_unpack,
    error_handler,
    get_child_items,
    get_first_revision_date,
    handle_store_exceptions,
    raise_operation_error,
)
from openprocurement.api.validation import validate_json_data
from openprocurement.tender.core.constants import (
    AUCTION_STAND_STILL_TIME,
    BIDDER_TIME,
    SERVICE_TIME,
)
from openprocurement.tender.core.procedure.context import get_bid, get_request
from openprocurement.tender.core.procedure.mask import TENDER_MASK_MAPPING
from openprocurement.tender.core.utils import QUICK, calculate_tender_date
from openprocurement.tender.openua.constants import AUCTION_PERIOD_TIME

LOGGER = getLogger(__name__)


def dt_from_iso(string):
    """
    datetime.fromisofomat() works fine if we don't change the object
    it add a static offset that is not aware of day light saving time
    tzinfo=datetime.timezone(datetime.timedelta(seconds=10800))
    and if we add timedelta +100 days, the result will be
    "2021-08-03T10:29:47.976944+03:00"
    not
    "2021-08-03T09:29:47.976944+02:00"
    :param string:
    :return:
    """
    dt = datetime.fromisoformat(string)
    dt = dt.astimezone(tz=TZ)
    return dt


def set_ownership(item, request, with_transfer=True):
    if not item.get("owner"):  # ???
        item["owner"] = request.authenticated_userid
    token = uuid4().hex
    item["owner_token"] = token
    access = {"token": token}
    if with_transfer:
        transfer = uuid4().hex
        item["transfer_token"] = sha512(transfer.encode("utf-8")).hexdigest()
        access["transfer"] = transfer
    return access


def save_tender(
    request,
    modified: bool = True,
    insert: bool = False,
    tender: dict = None,
    tender_src: dict = None,
) -> bool:
    if tender is None:
        tender = request.validated["tender"]
    if tender_src is None:
        tender_src = request.validated["tender_src"]

    patch = get_revision_changes(tender, tender_src)
    if patch:
        now = get_now()
        append_tender_revision(request, tender, patch, now)
        old_date_modified = tender.get("dateModified", now.isoformat())
        with handle_store_exceptions(request):
            request.registry.mongodb.tenders.save(
                tender,
                insert=insert,
                modified=modified,
            )
            LOGGER.info(
                "Saved tender {}: dateModified {} -> {}".format(
                    tender["_id"], old_date_modified, tender["dateModified"]
                ),
                extra=context_unpack(request, {"MESSAGE_ID": "save_tender"}, {"RESULT": tender["_rev"]}),
            )
            return True
    return False


def append_tender_revision(request, tender, patch, date):
    status_changes = [
        p
        for p in patch
        if all([not p["path"].startswith("/bids/"), p["path"].endswith("/status"), p["op"] == "replace"])
    ]
    for change in status_changes:
        obj = resolve_pointer(tender, change["path"].replace("/status", ""))
        if obj and hasattr(obj, "date"):
            date_path = change["path"].replace("/status", "/date")
            if obj.date and not any(p for p in patch if date_path == p["path"]):
                patch.append({"op": "replace", "path": date_path, "value": obj.date.isoformat()})
            elif not obj.date:
                patch.append({"op": "remove", "path": date_path})
            obj.date = date
    return append_revision(request, tender, patch)


def set_mode_test_titles(item):
    for key, prefix in (
        ("title", "ТЕСТУВАННЯ"),
        ("title_en", "TESTING"),
        ("title_ru", "ТЕСТИРОВАНИЕ"),
    ):
        if not item.get(key) or not item[key].startswith(f"[{prefix}]"):
            item[key] = f"[{prefix}] {item.get(key) or ''}"


# PATCHING ---
def apply_tender_patch(request, data, src, save=True, modified=True):
    patch = apply_data_patch(src, data)
    # src now contains changes,
    # it should link to request.validated["tender"]
    if patch and save:
        return save_tender(request, modified=modified)


# --- PATCHING


def submission_method_details_includes(substr, tender):
    details = tender.get("submissionMethodDetails")
    if details:
        substrs = substr if isinstance(substr, (tuple, list)) else (substr,)
        return any(substr in details for substr in substrs)
    return False


def normalize_should_start_after(start_after, tender):
    if submission_method_details_includes(QUICK, tender):
        return start_after
    return calc_normalized_datetime(start_after, ceil=True)


def contracts_allow_to_complete(contracts) -> bool:
    active_exists = False
    for contract in contracts:
        if contract.get("status") == "pending":
            return False
        if contract.get("status") == "active":
            active_exists = True
    return active_exists


def get_contracts_values_related_to_patched_contract(contracts, patched_contract_id, updated_value, award_id):
    _contracts_values = []

    for contract in contracts:
        if contract.get("status") != "cancelled" and contract.get("awardID") == award_id:
            if contract.get("id") != patched_contract_id:
                _contracts_values.append(contract.get("value", {}))
            else:
                _contracts_values.append(updated_value)
    return _contracts_values


def find_item_by_id(list_items: list, find_id: str) -> dict:
    for item in list_items:
        if item.get("id") == find_id:
            return item
    return {}


def get_criterion_requirement(tender, requirement_id) -> Optional[dict]:
    for criteria in tender.get("criteria", ""):
        for group in criteria.get("requirementGroups", ""):
            for req in group.get("requirements", ""):
                if req["id"] == requirement_id:
                    return criteria


def bid_in_invalid_status() -> Optional[bool]:
    request = get_request()
    if "/bids" not in request.url:
        return
    json_data = get_json_data()
    status = json_data.get("status") if isinstance(json_data, dict) else None
    if not status:
        bid = get_bid()
        status = bid["status"] if bid else "draft"
    return status in ("deleted", "invalid", "invalid.pre-qualification", "unsuccessful", "draft")


def validate_field(
    data,
    field,
    before=None,
    enabled=True,
    required=True,
    rogue=True,
    default=None,
):
    request = get_request()
    if before is not None and before.get(field) is not None:
        # in case if field is already set in old tender before this rule applied
        # we should allow to change it or remove
        rogue = False

    # field is enabled (or optional)
    if enabled is True and data.get(field) is None:
        if default is not None:
            data[field] = default
        elif required is True:
            raise_operation_error(
                request,
                ["This field is required."],
                status=422,
                location="body",
                name=field,
            )

    # field is disabled (or optional)
    if enabled is False and data.get(field) is not None:
        if rogue is True:
            raise_operation_error(
                request,
                ["Rogue field."],
                status=422,
                location="body",
                name=field,
            )


def get_bids_before_auction_results(tender):
    request = get_request()
    initial_doc = request.validated["tender_src"]
    auction_revisions = (
        revision for revision in reversed(tender.get("revisions", [])) if revision["author"] == "auction"
    )
    for revision in auction_revisions:
        try:
            initial_doc = apply_json_patch(initial_doc, revision["changes"])
        except (JsonPointerException, JsonPatchException) as e:
            LOGGER.exception(e, extra=context_unpack(request, {"MESSAGE_ID": "fail_get_tendering_bids"}))
    return deepcopy(initial_doc["bids"])


def tender_created_after(dt):
    tender_created = get_first_revision_date(get_tender(), default=get_now())
    return tender_created > dt


def tender_created_before(dt):
    tender_created = get_first_revision_date(get_tender(), default=get_now())
    return tender_created < dt


def tender_created_in(dt_from, dt_to):
    return tender_created_after(dt_from) and tender_created_before(dt_to)


def tender_created_after_2020_rules():
    return tender_created_after(RELEASE_2020_04_19)


def filter_features(features, items, lot_ids=None):
    lot_ids = lot_ids or [None]
    lot_items = [i["id"] for i in items if i.get("relatedLot") in lot_ids]  # all items in case of non-lot tender
    features = [
        feature
        for feature in (features or tuple())
        if any(
            (
                feature["featureOf"] == "tenderer",
                feature["featureOf"] == "lot" and feature["relatedItem"] in lot_ids,
                feature["featureOf"] == "item" and feature["relatedItem"] in lot_items,
            )
        )
    ]  # all features in case of non-lot tender
    return features


def activate_bids(bids):
    for bid in bids:
        lot_values = bid.get("lotValues", "")
        if lot_values:
            for lot_value in lot_values:
                lot_value["status"] = "active"
        if bid["status"] == "pending":
            bid["status"] = "active"
    return bids


def is_new_contracting():
    tender = get_tender()
    tender_type = tender.get("procurementMethodType", "")

    if tender_type == "esco":
        return False

    return True


def find_lot(tender, lot_id):
    for lot in tender.get("lots", ""):
        if lot and lot["id"] == lot_id:
            return lot


def validate_features_custom_weight(data, features, max_sum):
    if features:
        if data["lots"]:
            if any(
                [
                    round(vnmax(filter_features(features, data["items"], lot_ids=[lot["id"]])), 15) > max_sum
                    for lot in data["lots"]
                ]
            ):
                raise ValidationError(
                    "Sum of max value of all features for lot should be "
                    "less then or equal to {:.0f}%".format(max_sum * 100)
                )
        else:
            if round(vnmax(features), 15) > max_sum:
                raise ValidationError(
                    "Sum of max value of all features should be " "less then or equal to {:.0f}%".format(max_sum * 100)
                )


def round_up_to_ten(value):
    return int(math.ceil(value / 10.0) * 10)


def restrict_value_to_bounds(value, min_value, max_value):
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def check_auction_period(period, tender):
    if period and period.get("startDate") and period.get("shouldStartAfter"):
        start = parse_date(period["shouldStartAfter"])
        should_start = calculate_tender_date(start, AUCTION_PERIOD_TIME, tender=tender, working_days=True)
        start = period["startDate"]
        if isinstance(start, str):
            start = parse_date(period["startDate"])
        return start > should_start
    return False


def calc_auction_end_time(bids, start):
    return start + bids * BIDDER_TIME + SERVICE_TIME + AUCTION_STAND_STILL_TIME


def generate_tender_id(request):
    now = get_now()
    uid = f"tender_{now.date().isoformat()}"
    index = request.registry.mongodb.get_next_sequence_value(uid)
    return "UA-{:04}-{:02}-{:02}-{:06}-a".format(now.year, now.month, now.day, index)


def extract_complaint_type(request):
    """
    request method
    determines which type of complaint is processed
    returns complaint_type
    used in isComplaint route predicate factory
    to match complaintType predicate
    to route to Claim or Complaint view
    """

    path = extract_path(request)
    matchdict = matchdict_from_path(path)

    complaint_id = matchdict.get("complaint_id")
    # extract complaint type from POST request
    if not complaint_id:
        data = validate_json_data(request)
        complaint_type = data.get("type", None)
        # before RELEASE_2020_04_19 claim type is default if no value provided
        if not complaint_type:
            complaint_type = "claim"
        return complaint_type

    # extract complaint type from tender for PATCH request
    complaint_resource_names = ["award", "qualification"]
    for complaint_resource_name in complaint_resource_names:
        complaint_resource = _extract_resource(request, matchdict, request.tender_doc, complaint_resource_name)
        if complaint_resource:
            break

    if not complaint_resource:
        complaint_resource = request.tender_doc

    complaint = _extract_resource(request, matchdict, complaint_resource, "complaint")
    return complaint.get("type")


def extract_path(request):
    try:
        # empty if mounted under a path in mod_wsgi, for example
        path = decode_path_info(request.environ["PATH_INFO"] or "/")
    except KeyError:
        path = "/"
    except UnicodeDecodeError as e:
        raise URLDecodeError(e.encoding, e.object, e.start, e.end, e.reason)
    return path


def extract_tender_id(request):
    if request.matchdict and "tender_id" in request.matchdict:
        return request.matchdict.get("tender_id")

    path = extract_path(request)
    # extract tender id
    parts = path.split("/")
    if len(parts) < 5 or parts[3] != "tenders":
        return
    tender_id = parts[4]
    return tender_id


def extract_tender_doc(request):
    tender_id = extract_tender_id(request)
    if tender_id:
        doc = request.registry.mongodb.tenders.get(tender_id)
        if doc is None:
            request.errors.add("url", "tender_id", "Not Found")
            request.errors.status = 404
            raise error_handler(request)

        # wartime measures
        mask_object_data_deprecated(request, doc)
        mask_object_data(request, doc, TENDER_MASK_MAPPING)

        return doc


def matchdict_from_path(path, root_resource="tenders"):
    path_parts = path.split("/")
    start_index = path_parts.index(root_resource)
    resource_path = path_parts[start_index:]
    return {"{}_id".format(k[:-1]): v for k, v in zip(resource_path[::2], resource_path[1::2])}


def _extract_resource(request, matchdict, parent_resource, resource_name):
    resource_id = matchdict.get(f'{resource_name}_id')
    if resource_id:
        resources = get_child_items(parent_resource, f'{resource_name}s', resource_id)
        if not resources:
            request.errors.add("url", f'{resource_name}_id', "Not Found")
            request.errors.status = 404
            raise error_handler(request)
        return resources[-1]
    return None


def get_supplier_contract(contracts, tenderers):
    for contract in contracts:
        if contract["status"] == "active":
            for supplier in contract.get("suppliers", ""):
                for tenderer in tenderers:
                    if supplier["identifier"]["id"] == tenderer["identifier"]["id"]:
                        return contract


def extract_document_id(request):
    path = extract_path(request)
    if "documents" in path:
        matchdict = matchdict_from_path(path, root_resource="documents")
        return matchdict.get("document_id")


def is_multi_currency_tender(check_funders=False):
    # for old contracting api, there is no tender in request.
    # But anyway multi currency can be only in belowThreshold, competitiveOrdering and new contracting
    if tender := get_tender():
        return tender["config"]["valueCurrencyEquality"] is False and (tender.get("funders") or not check_funders)


def was_changed_after_approve_review_request(tender: dict, review_request_date: dict) -> bool:
    excluded_changed_field = ("questions", "tenderPeriod", "next_check", "reviewRequests")

    request = get_request()
    tender_src = request.validated["tender_src"]

    changes = get_revision_changes(tender, tender_src)
    revisions = [{"date": get_now().isoformat(), "changes": changes}]
    revisions.extend(tender.get("revisions", [])[::-1])

    for rev in revisions:
        if review_request_date >= parse_date(rev["date"]):
            break

        for change in rev.get("changes", ""):
            path = change.get("path", "")
            if path and path.split("/")[1] not in excluded_changed_field:
                return True

    return False


def check_is_waiting_for_inspector_approve(tender: dict, lot_id=None, valid_statuses=None) -> bool:
    if not valid_statuses:
        return False

    status = tender.get("status", "")
    inspector = tender.get("inspector")

    if status not in valid_statuses or not inspector:
        return False

    rev_reqs = [i for i in tender.get("reviewRequests", []) if i.get("lotID") == lot_id and i["tenderStatus"] == status]

    if not rev_reqs:
        return True

    rev_req = rev_reqs[-1]

    return not rev_req.get("approved") or not rev_req.get("is_valid")


def check_is_tender_waiting_for_inspector_approve(tender: dict, lot_id=None) -> bool:
    return check_is_waiting_for_inspector_approve(tender, lot_id, valid_statuses=["active.enquiries"])


def check_is_contract_waiting_for_inspector_approve(tender: dict, lot_id=None) -> bool:
    return check_is_waiting_for_inspector_approve(
        tender, lot_id, valid_statuses=["active.qualification", "active.awarded"]
    )
