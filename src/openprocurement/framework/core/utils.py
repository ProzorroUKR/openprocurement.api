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
)
from openprocurement.framework.core.traversal import factory
from openprocurement.tender.core.utils import ACCELERATOR_RE

LOGGER = getLogger("openprocurement.framework.core")
ENQUIRY_PERIOD_DURATION = 10
SUBMISSION_STAND_STILL_DURATION = 30

frameworksresource = partial(resource, error_handler=error_handler, factory=factory)


class isFramework(object):
    """ Route predicate. """

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return "frameworkType = %s" % (self.val,)

    phash = text

    def __call__(self, context, request):
        if request.framework is not None:
            return getattr(request.framework, "frameworkType", None) == self.val
        return False


def register_framework_frameworkType(config, model):
    """Register a framework frameworkType.
    :param config:
        The pyramid configuration object that will be populated.
    :param model:
        The framework model class
    """
    config.registry.framework_frameworkTypes[model.frameworkType.default] = model


def framework_from_data(request, data, raise_error=True, create=True):
    frameworkType = data.get("frameworkType", "electronicCatalogue")
    model = request.registry.framework_frameworkTypes.get(frameworkType)
    if model is None and raise_error:
        request.errors.add("data", "frameworkType", "Not implemented")
        request.errors.status = 415
        raise error_handler(request.errors)
    update_logging_context(request, {"framework_type": frameworkType})
    if model is not None and create:
        if request.environ.get("REQUEST_METHOD") == "GET" and data.get("revisions"):
            # to optimize get requests to frameworks with many revisions
            copy_data = dict(**data)  # changing of the initial dict is a bad practice
            copy_data["revisions"] = data["revisions"][:1]  # leave first revision for validations
            model = model(copy_data)
        else:
            model = model(data)
    return model


def extract_doc_adapter(request, framework_id):
    db = request.registry.db
    doc = db.get(framework_id)
    if doc is None or doc.get("doc_type") != "Framework":
        request.errors.add("url", "framework_id", "Not Found")
        request.errors.status = 404
        raise error_handler(request.errors)

    return request.framework_from_data(doc)


def extract_doc(request):
    try:
        # empty if mounted under a path in mod_wsgi, for example
        path = decode_path_info(request.environ["PATH_INFO"] or "/")
    except KeyError:
        path = "/"
    except UnicodeDecodeError as e:
        raise URLDecodeError(e.encoding, e.object, e.start, e.end, e.reason)

    framework_id = ""
    # extract framework id
    parts = path.split("/")
    if len(parts) < 4 or parts[3] != "frameworks":
        return

    framework_id = parts[4]
    return extract_doc_adapter(request, framework_id)


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
    return "UA-{:04}-{:02}-{:02}-{:06}{}".format(
        ctime.year, ctime.month, ctime.day, index, server_id and "-" + server_id
    )


def save_framework(request):
    framework = request.validated["framework"]

    if framework.mode == u"test":
        set_modetest_titles(framework)

    patch = get_revision_changes(framework.serialize("plain"), request.validated["framework_src"])
    if patch:
        now = get_now()
        append_framework_revision(request, framework, patch, now)

        old_date_modified = framework.dateModified
        if getattr(framework, "modified", True):
            framework.dateModified = now

        with handle_store_exceptions(request):
            framework.store(request.registry.db)
            LOGGER.info(
                "Saved framework {}: dateModified {} -> {}".format(
                    framework.id,
                    old_date_modified and old_date_modified.isoformat(),
                    framework.dateModified.isoformat()
                ),
                extra=context_unpack(request, {"MESSAGE_ID": "save_framework"}, {"RESULT": framework.rev}),
            )
            return True


def get_framework_accelerator(context):
    if context and "submissionMethodDetails" in context and context["submissionMethodDetails"]:
        re_obj = ACCELERATOR_RE.search(context["submissionMethodDetails"])
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


def apply_patch(request, data=None, save=True, src=None):
    data = request.validated["data"] if data is None else data
    patch = data and apply_data_patch(src or request.context.serialize(), data)
    if patch:
        request.context.import_data(patch)
        if save:
            return save_framework(request)


def append_framework_revision(request, framework, patch, date):
    status_changes = [p for p in patch if all([
        p["path"].endswith("/status"),
        p["op"] == "replace"
    ])]
    for change in status_changes:
        obj = resolve_pointer(framework, change["path"].replace("/status", ""))
        if obj and hasattr(obj, "date"):
            date_path = change["path"].replace("/status", "/date")
            if obj.date and not any([p for p in patch if date_path == p["path"]]):
                patch.append({"op": "replace", "path": date_path, "value": obj.date.isoformat()})
            elif not obj.date:
                patch.append({"op": "remove", "path": date_path})
            obj.date = date
    return append_revision(request, framework, patch)


def framework_serialize(request, framework_data, fields):
    framework = request.framework_from_data(framework_data, raise_error=False)
    framework.__parent__ = request.context
    return dict([(i, j) for i, j in framework.serialize("view").items() if i in fields])
