from openprocurement.api.utils import handle_store_exceptions, context_unpack
from openprocurement.api.auth import extract_access_token
from openprocurement.api.constants import (
    SANDBOX_MODE,
    TZ,
    NORMALIZE_SHOULD_START_AFTER,
)
from openprocurement.tender.core.procedure.context import get_now
from openprocurement.tender.core.utils import QUICK
from dateorro import calc_normalized_datetime
from jsonpatch import make_patch, apply_patch
from jsonpointer import resolve_pointer
from hashlib import sha512
from uuid import uuid4
from logging import getLogger
from datetime import datetime
import re


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


def get_first_revision_date(document, default=None):
    revisions = document.get("revisions") if document else None
    return datetime.fromisoformat(revisions[0]["date"]) if revisions else default


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


def save_tender(request, modified: bool = True, insert: bool = False) -> bool:
    tender = request.validated["tender"]
    patch = get_revision_changes(tender, request.validated["tender_src"])
    if patch:
        now = get_now()
        append_tender_revision(request, tender, patch, now)

        old_date_modified = tender.get("dateModified", now.isoformat())
        if modified:
            tender["dateModified"] = now.isoformat()

        with handle_store_exceptions(request):
            request.registry.mongodb.tenders.save(
                tender,
                insert=insert,
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
        if not item.get(key) or prefix not in item[key]:
            item[key] = f"[{prefix}] {item.get(key) or ''}"


# GETTING/SETTING sub documents ---

def get_items(request, parent, key, uid):
    items = tuple(i for i in parent.get(key, "") if i["id"] == uid)
    if items:
        return items
    else:
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
def is_item_owner(request, item):
    acc_token = extract_access_token(request)
    return request.authenticated_userid == item["owner"] and acc_token == item["owner_token"]
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


def submission_search(pattern, tender):
    patterns = pattern if isinstance(pattern, (tuple, list)) else (pattern,)
    details = tender.get("submissionMethodDetails")
    if SANDBOX_MODE and details:
        return any(re.search(pattern, details) for pattern in patterns)
    return False


def normalize_should_start_after(start_after, tender):
    if submission_search(QUICK, tender):
        return start_after
    if tender.get("enquiryPeriod", {}).get("startDate"):
        date = dt_from_iso(tender["enquiryPeriod"]["startDate"])
    else:
        date = get_now()
    if NORMALIZE_SHOULD_START_AFTER < date:
        return calc_normalized_datetime(start_after, ceil=True)
    return start_after


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
