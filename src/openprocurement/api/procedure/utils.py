from datetime import datetime
from decimal import Decimal
from hashlib import sha512
from logging import getLogger
from uuid import uuid4

import pytz
from ciso8601 import parse_datetime
from jsonpatch import apply_patch, make_patch

from openprocurement.api.auth import extract_access_token
from openprocurement.api.constants import (
    CPV_DEFAULT_PREFIX_LENGTH,
    CPV_PHARM_PREFIX,
    CPV_PHARM_PREFIX_LENGTH,
)
from openprocurement.api.context import get_now

LOGGER = getLogger(__name__)


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
                prepare_patch(
                    changes,
                    orig[i],
                    patch[i],
                    "{}/{}".format(basepath, i),
                    none_means_remove=none_means_remove,
                )
            elif patch[i] is None and none_means_remove:
                pass  # already deleted
            else:
                changes.append(
                    {
                        "op": "add",
                        "path": "{}/{}".format(basepath, i),
                        "value": patch[i],
                    }
                )
    elif isinstance(patch, list):
        if len(patch) < len(orig):
            for i in reversed(list(range(len(patch), len(orig)))):
                changes.append({"op": "remove", "path": "{}/{}".format(basepath, i)})
        for i, j in enumerate(patch):
            if len(orig) > i:
                prepare_patch(
                    changes,
                    orig[i],
                    patch[i],
                    "{}/{}".format(basepath, i),
                    none_means_remove=none_means_remove,
                )
            else:
                changes.append({"op": "add", "path": "{}/{}".format(basepath, i), "value": j})
    elif none_means_remove and patch is None:
        changes.append({"op": "remove", "path": basepath})
    else:
        for x in make_patch(orig, patch).patch:
            x["path"] = "{}{}".format(basepath, x["path"])
            changes.append(x)


def generate_revision(obj, patch, author, date=None):
    return {
        "author": author,
        "changes": patch,
        "rev": obj.get("_rev"),
        "date": (date or get_now()).isoformat(),
    }


def append_revision(request, obj, patch, date=None):
    author = request.authenticated_userid
    revision_data = generate_revision(obj, patch, author, date)
    if "revisions" not in obj:
        obj["revisions"] = []
    obj["revisions"].append(revision_data)
    return obj["revisions"]


def get_revision_changes(dst, src):
    return make_patch(dst, src).patch


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


def is_const_active(constant):
    return get_now() > constant


def get_first_revision_date(document, default=None):
    revisions = document.get("revisions") if document else None
    return datetime.fromisoformat(revisions[0]["date"]) if revisions else default


def is_obj_const_active(obj, constant):
    return get_first_revision_date(obj, default=get_now()) > constant


def is_item_owner(request, item, token_field_name="owner_token"):
    acc_token = extract_access_token(request)
    return request.authenticated_userid == item["owner"] and acc_token == item[token_field_name]


def get_items(request, parent, key, uid, raise_404=True):
    items = tuple(i for i in parent.get(key, "") if i["id"] == uid)
    if items:
        return items
    elif raise_404:
        # pylint: disable-next=import-outside-toplevel, cyclic-import
        from openprocurement.api.utils import error_handler

        obj_name = "document" if "Document" in key else key.rstrip("s")
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


def get_cpv_prefix_length(classifications):
    """
    For pharm products we should use 3 digits prefix
    and usually 4 digits prefix for other products
    """
    for classification in classifications:
        if classification["id"].startswith(CPV_PHARM_PREFIX):
            return CPV_PHARM_PREFIX_LENGTH

    return CPV_DEFAULT_PREFIX_LENGTH


def get_cpv_uniq_prefixes(classifications, prefix_length):
    return {i["id"][:prefix_length] for i in classifications}


def parse_date(value, default_timezone=pytz.utc):
    date = parse_datetime(value)
    if not date.tzinfo:
        date = default_timezone.localize(date)
    return date


def to_decimal(value):
    """
    Convert other to Decimal.
    """
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int) or isinstance(value, str):
        return Decimal(value)
    if isinstance(value, float):
        return Decimal(repr(value))

    raise TypeError("Unable to convert %s to Decimal" % value)
