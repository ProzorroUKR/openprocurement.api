from datetime import timedelta
from hashlib import sha512
from logging import getLogger

from jsonpointer import resolve_pointer
from pyramid.compat import decode_path_info
from pyramid.exceptions import URLDecodeError

from openprocurement.api.auth import extract_access_token
from openprocurement.api.context import get_now
from openprocurement.api.mask import mask_object_data
from openprocurement.api.mask_deprecated import mask_object_data_deprecated
from openprocurement.api.procedure.utils import append_revision, get_revision_changes
from openprocurement.api.utils import (
    context_unpack,
    error_handler,
    handle_store_exceptions,
)
from openprocurement.framework.core.constants import DAYS_TO_UNSUCCESSFUL_STATUS
from openprocurement.framework.core.procedure.mask import (
    AGREEMENT_MASK_MAPPING,
    QUALIFICATION_MASK_MAPPING,
    SUBMISSION_MASK_MAPPING,
)
from openprocurement.framework.core.utils import calculate_framework_date
from openprocurement.tender.core.procedure.utils import dt_from_iso

LOGGER = getLogger(__name__)


def append_obj_revision(request, obj, patch, date):
    status_changes = [p for p in patch if all([p["path"].endswith("/status"), p["op"] == "replace"])]
    changed_obj = obj
    for change in status_changes:
        changed_obj = resolve_pointer(obj, change["path"].replace("/status", ""))
        if changed_obj and hasattr(changed_obj, "date") and hasattr(changed_obj, "revisions"):
            date_path = change["path"].replace("/status", "/date")
            if changed_obj.date and not any(p for p in patch if date_path == p["path"]):
                patch.append({"op": "replace", "path": date_path, "value": changed_obj.date.isoformat()})
            elif not changed_obj.date:
                patch.append({"op": "remove", "path": date_path})
            changed_obj.date = date
        else:
            changed_obj = obj
    return append_revision(request, changed_obj, patch)


def save_object(
    request, obj_name, modified: bool = True, insert: bool = False, additional_obj_names="", raise_error_handler=False
) -> bool:
    obj = request.validated[obj_name]
    patch = get_revision_changes(obj, request.validated[f"{obj_name}_src"])
    if patch:
        now = get_now()
        append_obj_revision(request, obj, patch, now)
        old_date_modified = obj.get("dateModified", now.isoformat())

        for i in additional_obj_names:
            if i in request.validated:
                request.validated[i]["dateModified"] = now

        with handle_store_exceptions(request, raise_error_handler=raise_error_handler):
            collection = getattr(request.registry.mongodb, f"{obj_name}s")
            collection.save(obj, insert=insert, modified=modified)
            LOGGER.info(
                f"Saved {obj_name} {obj['_id']}: dateModified {old_date_modified} -> {obj['dateModified']}",
                extra=context_unpack(request, {"MESSAGE_ID": f"save_{obj_name}"}, {"RESULT": obj["_rev"]}),
            )
            return True
    return False


def extract_path(request):
    try:
        # empty if mounted under a path in mod_wsgi, for example
        path = decode_path_info(request.environ["PATH_INFO"] or "/")
    except KeyError:
        path = "/"
    except UnicodeDecodeError as e:
        raise URLDecodeError(e.encoding, e.object, e.start, e.end, e.reason)
    return path


def extract_object_id(request, obj_name):
    if request.matchdict and f"{obj_name}_id" in request.matchdict:
        return request.matchdict.get(f"{obj_name}_id")

    path = extract_path(request)
    # extract tender id
    parts = path.split("/")
    if len(parts) < 5 or parts[3] != f"{obj_name}s":
        return
    object_id = parts[4]
    return object_id


def extract_object_doc(request, obj_name, mask_mapping=None):
    object_id = extract_object_id(request, obj_name)
    if object_id:
        doc = getattr(request.registry.mongodb, f"{obj_name}s").get(object_id)
        if doc is None:
            request.errors.add("url", f"{obj_name}_id", "Not Found")
            request.errors.status = 404
            raise error_handler(request)

        # wartime measures
        mask_object_data_deprecated(request, doc)
        mask_object_data(request, doc, mask_mapping=mask_mapping)

        return doc


def extract_framework_doc(request):
    return extract_object_doc(request, "framework")


def extract_submission_doc(request):
    return extract_object_doc(request, "submission", mask_mapping=SUBMISSION_MASK_MAPPING)


def extract_qualification_doc(request):
    return extract_object_doc(request, "qualification", mask_mapping=QUALIFICATION_MASK_MAPPING)


def extract_agreement_doc(request):
    return extract_object_doc(request, "agreement", mask_mapping=AGREEMENT_MASK_MAPPING)


def get_framework_unsuccessful_status_check_date(framework):
    if period_start := framework.get("period", {}).get("startDate"):
        return calculate_framework_date(
            dt_from_iso(period_start),
            timedelta(days=DAYS_TO_UNSUCCESSFUL_STATUS),
            framework,
            working_days=True,
            ceil=True,
        )


def get_framework_number_of_submissions(request, framework):
    framework_id = framework.get("_id") if isinstance(framework, dict) else framework.id
    result = request.registry.mongodb.submissions.count_total_submissions_by_framework_id(framework_id)
    return result


# ACL ---
def is_framework_owner(request, item):
    acc_token = extract_access_token(request)
    return request.authenticated_userid == item["framework_owner"] and acc_token == item["framework_token"]


def is_tender_owner(request, item):
    acc_token = extract_access_token(request)
    if len(acc_token) == 32 and len(item["tender_token"]) > 32:
        acc_token = sha512(acc_token.encode()).hexdigest()
    return request.authenticated_userid == item["owner"] and acc_token == item["tender_token"]


# --- ACL
