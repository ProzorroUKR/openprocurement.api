import math
from copy import deepcopy
from typing import Optional

from barbecue import vnmax
from pyramid.compat import decode_path_info
from pyramid.exceptions import URLDecodeError
from schematics.exceptions import ValidationError

from openprocurement.api.context import (
    get_json_data,
    get_now,
)
from openprocurement.api.mask import mask_object_data
from openprocurement.api.traversal import get_child_items
from openprocurement.api.utils import (
    handle_store_exceptions,
    context_unpack,
    raise_operation_error,
    get_first_revision_date,
    parse_date,
    get_now,
    error_handler,
)
from openprocurement.api.auth import extract_access_token
from openprocurement.api.constants import (
    TZ,
    RELEASE_2020_04_19,
)
from openprocurement.api.validation import validate_json_data
from openprocurement.tender.core.constants import BIDDER_TIME, SERVICE_TIME, AUCTION_STAND_STILL_TIME
from openprocurement.tender.core.procedure.context import (
    get_bid,
    get_request,
    get_tender,
)
from openprocurement.tender.core.utils import (
    QUICK,
    calculate_tender_date,
)
from dateorro import calc_normalized_datetime
from jsonpatch import (
    make_patch,
    apply_patch,
    apply_patch as apply_json_patch,
    JsonPatchException,
)
from jsonpointer import (
    resolve_pointer,
    JsonPointerException,
)
from hashlib import sha512
from uuid import uuid4
from logging import getLogger
from datetime import datetime

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


def set_ownership(item, request):
    if not item.get("owner"):  # ???
        item["owner"] = request.authenticated_userid
    token, transfer = uuid4().hex, uuid4().hex
    item["owner_token"] = token
    item["transfer_token"] = sha512(transfer.encode("utf-8")).hexdigest()
    access = {"token": token, "transfer": transfer}
    return access


def delete_nones(data: dict):
    for k, v in tuple(data.items()):
        if v is None:
            del data[k]


def save_tender(request, modified: bool = True, insert: bool = False, tender: dict = None, tender_src: dict = None) -> bool:
    if tender is None:
        tender = request.validated["tender"]
    if tender_src is None:
        tender_src = request.validated["tender_src"]

    set_tender_config(request, tender)
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
                    tender["_id"],
                    old_date_modified,
                    tender["dateModified"]
                ),
                extra=context_unpack(request, {"MESSAGE_ID": "save_tender"}, {"RESULT": tender["_rev"]}),
            )
            return True
    return False


def set_tender_config(request, tender):
    config = request.validated.get("tender_config", {})
    if config:
        tender["config"] = config


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


def append_revision(request, obj, patch):
    revision_data = {
        "author": request.authenticated_userid,
        "changes": patch,
        "rev": obj.get("_rev"),
        "date": get_now().isoformat(),
    }
    if "revisions" not in obj:
        obj["revisions"] = []
    obj["revisions"].append(revision_data)
    return obj["revisions"]


def get_revision_changes(dst, src):
    result = make_patch(dst, src).patch
    return result


def set_mode_test_titles(item):
    for key, prefix in (
        ("title", "ТЕСТУВАННЯ"),
        ("title_en", "TESTING"),
        ("title_ru", "ТЕСТИРОВАНИЕ"),
    ):
        if not item.get(key) or not item[key].startswith(f"[{prefix}]"):
            item[key] = f"[{prefix}] {item.get(key) or ''}"


# GETTING/SETTING sub documents ---

def get_items(request, parent, key, uid, raise_404=True):
    items = tuple(i for i in parent.get(key, "") if i["id"] == uid)
    if items:
        return items
    elif raise_404:
        from openprocurement.api.utils import error_handler
        obj_name = "document" if "Document" in key else key.rstrip('s')
        request.errors.add("url", f"{obj_name}_id", "Not Found")
        request.errors.status = 404
        raise error_handler(request)


def set_item(parent, key, uid, value):
    assert value["id"] == uid, "Assigning item by id with a different id ?"
    initial_list = parent.get(key, "")
    # in case multiple documents we update the latest
    for n, item in enumerate(reversed(initial_list), 1):
        if item["id"] == uid:
            initial_list[-1 * n] = value
            break
    else:
        raise AssertionError(f"Item with id {uid} unexpectedly not found")
# --- GETTING/SETTING/DELETING sub documents


# ACL ---
def is_item_owner(request, item, token_field_name="owner_token"):
    acc_token = extract_access_token(request)
    return request.authenticated_userid == item["owner"] and acc_token == item[token_field_name]
# --- ACL


# PATCHING ---
def apply_tender_patch(request, data, src, save=True, modified=True):
    patch = apply_data_patch(src, data)
    # src now contains changes,
    # it should link to request.validated["tender"]
    if patch and save:
        return save_tender(request, modified=modified)


def apply_data_patch(item, changes, none_means_remove=False):
    """
    :param item:
    :param changes:
    :param none_means_remove:  if True, passing for ex. {"period": {"startDate": None}}
    will actually delete field's value instead of replacing it with None
    :return:
    """
    patch_changes = []
    prepare_patch(patch_changes, item, changes, none_means_remove=none_means_remove)
    if not patch_changes:
        return {}
    r = apply_patch(item, patch_changes)
    return r


def prepare_patch(changes, orig, patch, basepath="", none_means_remove=False):
    if isinstance(patch, dict):
        for i in patch:
            if i in orig:
                prepare_patch(changes, orig[i], patch[i], "{}/{}".format(basepath, i),
                              none_means_remove=none_means_remove)
            elif patch[i] is None and none_means_remove:
                pass  # already deleted
            else:
                changes.append({"op": "add", "path": "{}/{}".format(basepath, i), "value": patch[i]})
    elif isinstance(patch, list):
        if len(patch) < len(orig):
            for i in reversed(list(range(len(patch), len(orig)))):
                changes.append({"op": "remove", "path": "{}/{}".format(basepath, i)})
        for i, j in enumerate(patch):
            if len(orig) > i:
                prepare_patch(changes, orig[i], patch[i], "{}/{}".format(basepath, i),
                              none_means_remove=none_means_remove)
            else:
                changes.append({"op": "add", "path": "{}/{}".format(basepath, i), "value": j})
    elif none_means_remove and patch is None:
        changes.append({"op": "remove", "path": basepath})
    else:
        for x in make_patch(orig, patch).patch:
            x["path"] = "{}{}".format(basepath, x["path"])
            changes.append(x)

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
        revision for revision in reversed(tender.get("revisions", []))
        if revision["author"] == "auction"
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
    lot_items = [
        i["id"]
        for i in items
        if i.get("relatedLot") in lot_ids
    ]  # all items in case of non-lot tender
    features = [
        feature
        for feature in (features or tuple())
        if any((
            feature["featureOf"] == "tenderer",
            feature["featureOf"] == "lot" and feature["relatedItem"] in lot_ids,
            feature["featureOf"] == "item" and feature["relatedItem"] in lot_items,
        ))
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


def find_lot(tender, lot_id):
    for lot in tender.get("lots", ""):
        if lot and lot["id"] == lot_id:
            return lot


def validate_features_custom_weight(data, features, max_sum):
    if features:
        if data["lots"]:
            if any([
                round(vnmax(filter_features(features, data["items"], lot_ids=[lot["id"]])), 15) > max_sum
                for lot in data["lots"]
            ]):
                raise ValidationError(
                    "Sum of max value of all features for lot should be "
                    "less then or equal to {:.0f}%".format(max_sum * 100)
                )
        else:
            if round(vnmax(features), 15) > max_sum:
                raise ValidationError(
                    "Sum of max value of all features should be "
                    "less then or equal to {:.0f}%".format(max_sum * 100)
                )


def round_up_to_ten(value):
    return int(math.ceil(value / 10.) * 10)


def restrict_value_to_bounds(value, min_value, max_value):
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def check_auction_period(period, tender):
    if period and period.get("startDate") and period.get("shouldStartAfter"):
        start = parse_date(period["shouldStartAfter"])
        should_start = calculate_tender_date(start, AUCTION_PERIOD_TIME, tender, True)
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
        mask_object_data(request, doc)

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
