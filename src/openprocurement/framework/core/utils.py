from functools import partial, wraps
from logging import getLogger
from time import sleep

from cornice.resource import resource
from couchdb import ResourceConflict
from dateorro import calc_datetime
from jsonpointer import resolve_pointer
from pyramid.compat import decode_path_info
from pyramid.exceptions import URLDecodeError

from openprocurement.api.constants import WORKING_DAYS
from openprocurement.api.utils import (
    error_handler,
    update_logging_context,
    set_modetest_titles,
    get_revision_changes,
    get_now,
    handle_store_exceptions,
    context_unpack,
    apply_data_patch,
    append_revision,
    get_doc_by_id,
    ACCELERATOR_RE,
    generate_id,
)
from openprocurement.framework.core.models import IAgreement
from openprocurement.framework.core.traversal import (
    framework_factory,
    submission_factory,
    qualification_factory,
    agreement_factory,
)

LOGGER = getLogger("openprocurement.framework.core")
ENQUIRY_PERIOD_DURATION = 10
SUBMISSION_STAND_STILL_DURATION = 30

frameworksresource = partial(resource, error_handler=error_handler, factory=framework_factory)
submissionsresource = partial(resource, error_handler=error_handler, factory=submission_factory)
qualificationsresource = partial(resource, error_handler=error_handler, factory=qualification_factory)
agreementsresource = partial(resource, error_handler=error_handler, factory=agreement_factory)


class isFramework(object):
    """Framework Route predicate. """

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return "frameworkType = %s" % (self.val,)

    phash = text

    def __call__(self, context, request):
        if request.framework is not None:
            return getattr(request.framework, "frameworkType", None) == self.val
        return False


class isSubmission(object):
    """Submission Route predicate. """

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return "submissionType = %s" % (self.val,)

    phash = text

    def __call__(self, context, request):
        if request.submission is not None:
            return getattr(request.submission, "submissionType", None) == self.val

        return False


class isQualification(object):
    """Qualification Route predicate. """

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return "qualificationType = %s" % (self.val,)

    phash = text

    def __call__(self, context, request):
        if request.qualification is not None:
            return getattr(request.qualification, "qualificationType", None) == self.val
        return False


class IsAgreement(object):
    """ Agreement route predicate. """

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return "agreementType = %s" % (self.val,)

    phash = text

    def __call__(self, context, request):
        if request.agreement is not None:
            return getattr(request.agreement, "agreementType", None) == self.val
        return False


def register_framework_frameworkType(config, model):
    """Register a framework frameworkType.
    :param config:
        The pyramid configuration object that will be populated.
    :param model:
        The framework model class
    """
    config.registry.framework_frameworkTypes[model.frameworkType.default] = model


def register_submission_submissionType(config, model):
    submission_type = model.submissionType.default
    config.registry.submission_submissionTypes[submission_type] = model


def register_qualification_qualificationType(config, model):
    qualification_type = model.qualificationType.default
    config.registry.qualification_qualificationTypes[qualification_type] = model


def register_agreement_agreementType(config, model):
    agreement_type = model.agreementType.default
    config.registry.agreement_agreementTypes[agreement_type] = model


def object_from_data(request, data, obj_name, raise_error=True, create=True):
    objType = data.get("%sType" % obj_name, "electronicCatalogue")
    model_types = getattr(request.registry, "%s_%sTypes" % (obj_name, obj_name))
    model = model_types.get(objType)
    if model is None and raise_error:
        request.errors.add("body", "%sType" % obj_name, "Not implemented")
        request.errors.status = 415
        raise error_handler(request)
    update_logging_context(request, {"%s_type" % obj_name: objType})
    if model is not None and create:
        model = model(data)
    return model


def framework_from_data(request, data, raise_error=True, create=True):
    return object_from_data(request, data, "framework", raise_error=raise_error, create=create)


def submission_from_data(request, data, raise_error=True, create=True):
    return object_from_data(request, data, "submission", raise_error=raise_error, create=create)


def qualification_from_data(request, data, raise_error=True, create=True):
    return object_from_data(request, data, "qualification", raise_error=raise_error, create=create)


def agreement_from_data(request, data, raise_error=True, create=True):
    if request.authenticated_role == "agreements":
        data["agreementType"] = "cfaua"
    if not data.get("agreementType") and raise_error:
        request.errors.add("data", "agreementType", "This field is required")
        request.errors.status = 422
        raise error_handler(request)

    return object_from_data(request, data, "agreement", raise_error=raise_error, create=create)


def extract_doc_adapter(request, doc_type, doc_id):
    doc_type_singular = doc_type[:-1]  # lower, without last symbol  "frameworks" --> "framework"
    doc = get_doc_by_id(request.registry.databases[doc_type], doc_type_singular.capitalize(), doc_id)
    if doc is None:
        request.errors.add("url", "%s_id" % doc_type_singular, "Not Found")
        request.errors.status = 404
        raise error_handler(request)
    # obsolete lowercase doc_type in agreements
    if doc is not None and doc.get("doc_type") == "agreement":
        request.errors.add("url", "agreement_id", "Archived")
        request.errors.status = 410
        raise error_handler(request)

    method = getattr(request, "%s_from_data" % doc_type_singular)
    return method(doc)


def extract_doc(request):
    try:
        # empty if mounted under a path in mod_wsgi, for example
        path = decode_path_info(request.environ["PATH_INFO"] or "/")
    except KeyError:
        path = "/"
    except UnicodeDecodeError as e:
        raise URLDecodeError(e.encoding, e.object, e.start, e.end, e.reason)

    # obj_id = ""
    # extract object id
    parts = path.split("/")
    if len(parts) < 4 or parts[3] not in ("frameworks", "submissions", "qualifications", "agreements"):
        return

    # obj_type = parts[3][0].upper() + parts[3][1:-1]
    obj_type = parts[3]
    obj_id = parts[4]
    return extract_doc_adapter(request, obj_type, obj_id)


def generate_framework_pretty_id(ctime, db, server_id=""):
    key = ctime.date().isoformat()
    prettyIDdoc = "frameworkPrettyID_" + server_id if server_id else "frameworkPrettyID"
    while True:
        try:
            prettyID = db.get(prettyIDdoc, {"_id": prettyIDdoc})
            index = prettyID.get(key, 1)
            prettyID[key] = index + 1
            db.save(prettyID)
        except ResourceConflict:  # pragma: no cover
            pass
        except Exception:  # pragma: no cover
            sleep(1)
        else:
            break
    return "UA-F-{:04}-{:02}-{:02}-{:06}{}".format(
        ctime.year, ctime.month, ctime.day, index, server_id and "-" + server_id
    )


def generate_agreementID(ctime, db, server_id=""):
    key = ctime.date().isoformat()
    prettyIDdoc = "agreementID_" + server_id if server_id else "agreementID"
    while True:
        try:
            agreementID = db.get(prettyIDdoc, {"_id": prettyIDdoc})
            index = agreementID.get(key, 1)
            agreementID[key] = index + 1
            db.save(agreementID)
        except ResourceConflict:  # pragma: no cover
            pass
        except Exception:  # pragma: no cover
            sleep(1)
        else:
            break
    return "UA-{:04}-{:02}-{:02}-{:06}{}".format(
        ctime.year, ctime.month, ctime.day, index, server_id and "-" + server_id
    )


def save_object(request, obj_name, with_test_mode=True):
    obj = request.validated[obj_name]

    if with_test_mode and obj.mode == "test":
        set_modetest_titles(obj)

    patch = get_revision_changes(obj.serialize("plain"), request.validated["%s_src" % obj_name])
    if patch:
        now = get_now()
        append_obj_revision(request, obj, patch, now)

        old_date_modified = obj.dateModified
        if getattr(obj, "modified", True):
            obj.dateModified = now

        with handle_store_exceptions(request):
            obj.store(request.registry.databases[f"{obj_name}s"])  # TODO a better way to specify db name?
            LOGGER.info(
                "Saved {} {}: dateModified {} -> {}".format(
                    obj_name,
                    obj.id,
                    old_date_modified and old_date_modified.isoformat(),
                    obj.dateModified.isoformat()
                ),
                extra=context_unpack(request, {"MESSAGE_ID": "save_{}".format(obj_name)}, {"RESULT": obj.rev}),
            )
            return True


def save_framework(request):
    return save_object(request, "framework")


def save_submission(request):
    return save_object(request, "submission", with_test_mode=False)


def save_qualification(request):
    return save_object(request, "qualification", with_test_mode=False)


def save_agreement(request):
    return save_object(request, "agreement", with_test_mode=False)


def get_framework_accelerator(context):
    if context and "frameworkDetails" in context and context["frameworkDetails"]:
        re_obj = ACCELERATOR_RE.search(context["frameworkDetails"])
        if re_obj and "accelerator" in re_obj.groupdict():
            return int(re_obj.groupdict()["accelerator"])
    return None


def acceleratable(wrapped):
    @wraps(wrapped)
    def wrapper(date_obj, timedelta_obj,  framework=None, working_days=False, calendar=WORKING_DAYS, **kwargs):
        accelerator = get_framework_accelerator(framework)
        if accelerator:
            return calc_datetime(date_obj, timedelta_obj, accelerator=accelerator)
        return wrapped(
            date_obj, timedelta_obj, framework=framework, working_days=working_days, calendar=calendar, **kwargs
        )
    return wrapper


def apply_patch(request, obj_name, data=None, save=True, src=None):
    save_map = {
        "framework": save_framework,
        "submission": save_submission,
        "qualification": save_qualification,
        "agreement": save_agreement,
    }

    data = request.validated["data"] if data is None else data
    patch = data and apply_data_patch(src or request.context.serialize(), data)
    if patch:
        # Can't be replaced to "obj_name in save_map" because obj_name for child patch same as for parent
        if request.context.__class__.__name__.lower() in save_map:
            request.validated[obj_name].import_data(patch)
        else:
            request.context.import_data(patch)
        if save:
            save_func = save_map.get(obj_name)
            return save_func(request)


def append_obj_revision(request, obj, patch, date):
    status_changes = [p for p in patch if all([
        p["path"].endswith("/status"),
        p["op"] == "replace"
    ])]
    changed_obj = obj
    for change in status_changes:
        changed_obj = resolve_pointer(obj, change["path"].replace("/status", ""))
        if changed_obj and hasattr(changed_obj, "date") and hasattr(changed_obj, "revisions"):
            date_path = change["path"].replace("/status", "/date")
            if changed_obj.date and not any([p for p in patch if date_path == p["path"]]):
                patch.append({"op": "replace", "path": date_path, "value": changed_obj.date.isoformat()})
            elif not changed_obj.date:
                patch.append({"op": "remove", "path": date_path})
            changed_obj.date = date
        else:
            changed_obj = obj
    return append_revision(request, changed_obj, patch)


def obj_serialize(request, framework_data, fields):
    obj = request.framework_from_data(framework_data, raise_error=False)
    obj.__parent__ = request.context
    return dict([(i, j) for i, j in obj.serialize("view").items() if i in fields])


def agreement_serialize(request, agreement_data, fields):
    agreement = request.agreement_from_data(agreement_data, raise_error=False)
    agreement.__parent__ = request.context
    return {i: j for i, j in agreement.serialize("view").items() if i in fields}


def get_submission_by_id(request, submission_id):
    return request.registry.databases.submissions.get(submission_id)


def get_framework_by_id(request, framework_id):
    return request.registry.databases.frameworks.get(framework_id)


def get_agreement_by_id(request, agreement_id):
    return request.registry.databases.agreements.get(agreement_id)


def set_agreement_ownership(item, request):
    item.owner_token = generate_id()


def get_agreement(model):
    while not IAgreement.providedBy(model):
        model = model.__parent__
    return model
