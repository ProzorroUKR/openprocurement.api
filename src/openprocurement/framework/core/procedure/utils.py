import urllib.parse
from hashlib import sha512
from logging import getLogger

from jsonpointer import resolve_pointer
from pyramid.exceptions import URLDecodeError

from openprocurement.api.auth import extract_access_token
from openprocurement.api.context import get_request_now
from openprocurement.api.mask import mask_object_data
from openprocurement.api.mask_deprecated import mask_object_data_deprecated
from openprocurement.api.procedure.utils import append_revision, get_revision_changes
from openprocurement.api.procedure.utils import save_object as base_save_object
from openprocurement.api.utils import error_handler
from openprocurement.framework.core.procedure.mask import (
    AGREEMENT_MASK_MAPPING,
    QUALIFICATION_MASK_MAPPING,
    SUBMISSION_MASK_MAPPING,
)

LOGGER = getLogger(__name__)


def extract_path(request):
    try:
        # empty if mounted under a path in mod_wsgi, for example
        path = urllib.parse.unquote(request.environ["PATH_INFO"] or "/")
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


def save_object(
    request,
    obj_name,
    modified: bool = True,
    insert: bool = False,
    additional_obj_names="",
    raise_error_handler=False,
) -> bool:
    obj = request.validated[obj_name]
    obj_src = request.validated[f"{obj_name}_src"]

    patch = get_revision_changes(obj, obj_src)
    if not patch:
        return False

    update_status_change_revision(obj, patch, get_request_now())
    append_revision(request, obj, patch)

    for i in additional_obj_names:
        if i in request.validated:
            request.validated[i]["dateModified"] = get_request_now()

    return base_save_object(
        request,
        obj_name,
        modified,
        insert,
        raise_error_handler,
    )


def update_status_change_revision(obj, patch, date):
    status_changes = [
        p
        for p in patch
        if all(
            [
                p["path"].endswith("/status"),
                p["op"] == "replace",
            ]
        )
    ]
    changed_obj = obj
    for change in status_changes:
        changed_obj = resolve_pointer(obj, change["path"].replace("/status", ""))
        if changed_obj and hasattr(changed_obj, "date") and hasattr(changed_obj, "revisions"):
            date_path = change["path"].replace("/status", "/date")
            if changed_obj.date and not any(p for p in patch if date_path == p["path"]):
                patch.append(
                    {
                        "op": "replace",
                        "path": date_path,
                        "value": changed_obj.date.isoformat(),
                    }
                )
            elif not changed_obj.date:
                patch.append(
                    {
                        "op": "remove",
                        "path": date_path,
                    }
                )
            changed_obj.date = date
        else:
            changed_obj = obj
    return changed_obj
