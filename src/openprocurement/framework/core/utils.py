from datetime import timedelta
from functools import wraps
from logging import getLogger
from dateorro import (
    calc_datetime,
    calc_normalized_datetime,
    calc_working_datetime,
)
from pyramid.compat import decode_path_info
from pyramid.exceptions import URLDecodeError

from openprocurement.api.constants import WORKING_DAYS, DST_AWARE_PERIODS_FROM, TZ
from openprocurement.api.utils import (
    error_handler,
    update_logging_context,
    get_now, get_registry_object,
)
from openprocurement.api.validation import validate_json_data
from openprocurement.tender.core.utils import ACCELERATOR_RE

LOGGER = getLogger("openprocurement.framework.core")
ENQUIRY_PERIOD_DURATION = 10
SUBMISSION_STAND_STILL_DURATION = 30
ENQUIRY_STAND_STILL_TIME = 3
DAYS_TO_UNSUCCESSFUL_STATUS = 20
MILESTONE_CONTRACT_STATUSES = {
    "ban": "suspended",
    "terminated": "terminated",
}


class FrameworkTypePredicate(object):
    """Framework Route predicate. """

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return "frameworkType = %s" % (self.val,)

    phash = text

    def __call__(self, context, request):
        if request.framework_doc is not None:
            return request.framework_doc.get("frameworkType", None) == self.val

        if request.method == "POST" and request.path.endswith("/frameworks"):
            data = validate_json_data(request)
            return data.get("frameworkType", "electronicCatalogue") == self.val

        return False


class SubmissionTypePredicate(object):
    """Submission Route predicate. """

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return "submissionType = %s" % (self.val,)

    phash = text

    def __call__(self, context, request):
        if request.submission_doc is not None:
            return request.submission_doc.get("submissionType", None) == self.val

        if request.method == "POST" and request.path.endswith("/submissions"):
            data = validate_json_data(request)
            return data.get("submissionType", "electronicCatalogue") == self.val

        return False


class QualificationTypePredicate(object):
    """Qualification Route predicate. """

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return "qualificationType = %s" % (self.val,)

    phash = text

    def __call__(self, context, request):
        if request.qualification_doc is not None:
            return request.qualification_doc.get("qualificationType", None) == self.val

        if request.method == "POST" and request.path.endswith("/qualifications"):
            data = validate_json_data(request)
            return data.get("qualificationType", "electronicCatalogue") == self.val

        return False


class AgreementTypePredicate(object):
    """ Agreement route predicate. """

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return "agreementType = %s" % (self.val,)

    phash = text

    def __call__(self, context, request):
        if request.agreement_doc is not None:
            return request.agreement_doc.get("agreementType", None) == self.val

        if request.method == "POST" and request.path.endswith("/agreements"):
            data = validate_json_data(request)
            return data.get("agreementType", "cfaua") == self.val

        return False


def register_framework_frameworkType(config, model):
    registry_object = get_registry_object(config.registry, "framework_frameworkTypes", default={})
    registry_object[model.frameworkType.default] = model


def register_submission_submissionType(config, model):
    registry_object = get_registry_object(config.registry, "submission_submissionTypes", default={})
    registry_object[model.submissionType.default] = model


def register_qualification_qualificationType(config, model):
    registry_object = get_registry_object(config.registry, "qualification_qualificationTypes", default={})
    registry_object[model.qualificationType.default] = model


def register_agreement_agreementType(config, model):
    registry_object = get_registry_object(config.registry, "agreement_agreementTypes", default={})
    registry_object[model.agreementType.default] = model


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
    collection = getattr(request.registry.mongodb, doc_type)
    doc = collection.get(doc_id)
    if doc is None:
        request.errors.add("url", "%s_id" % doc_type_singular, "Not Found")
        request.errors.status = 404
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
    if len(parts) < 5 or parts[3] not in ("frameworks", "submissions", "qualifications", "agreements"):
        return

    # obj_type = parts[3][0].upper() + parts[3][1:-1]
    obj_type = parts[3]
    obj_id = parts[4]
    return extract_doc_adapter(request, obj_type, obj_id)


def generate_framework_pretty_id(request):
    ctime = get_now().date()
    index = request.registry.mongodb.get_next_sequence_value(f"framework_{ctime.isoformat()}")
    return "UA-F-{:04}-{:02}-{:02}-{:06}".format(
        ctime.year, ctime.month, ctime.day, index,
    )


def generate_agreement_id(request):
    ctime = get_now().date()
    index = request.registry.mongodb.get_next_sequence_value(f"agreement_{ctime.isoformat()}")
    return "UA-{:04}-{:02}-{:02}-{:06}".format(
        ctime.year, ctime.month, ctime.day, index,
    )

def get_framework_accelerator(context):
    if context and "frameworkDetails" in context and context["frameworkDetails"]:
        re_obj = ACCELERATOR_RE.search(context["frameworkDetails"])
        if re_obj and "accelerator" in re_obj.groupdict():
            return int(re_obj.groupdict()["accelerator"])
    return None


def acceleratable(wrapped):
    @wraps(wrapped)
    def wrapper(date_obj, timedelta_obj, framework=None, working_days=False, calendar=WORKING_DAYS, **kwargs):
        accelerator = get_framework_accelerator(framework)
        if accelerator:
            return calc_datetime(date_obj, timedelta_obj, accelerator=accelerator)
        return wrapped(
            date_obj, timedelta_obj, framework=framework, working_days=working_days, calendar=calendar, **kwargs
        )

    return wrapper


@acceleratable
def calculate_framework_date(
    date_obj,
    timedelta_obj,
    framework=None,
    working_days=False,
    calendar=WORKING_DAYS,
    ceil=False,
):
    date_obj = calc_normalized_datetime(date_obj, ceil=ceil)
    if working_days:
        result_date_obj = calc_working_datetime(date_obj, timedelta_obj, calendar=calendar)
    else:
        result_date_obj = calc_datetime(date_obj, timedelta_obj)
    if date_obj > DST_AWARE_PERIODS_FROM:
        result_date_obj = TZ.localize(result_date_obj.replace(tzinfo=None))
    return result_date_obj


def get_framework_unsuccessful_status_check_date(framework):
    if framework.period and framework.period.startDate:
        return calculate_framework_date(
            framework.period.startDate, timedelta(days=DAYS_TO_UNSUCCESSFUL_STATUS),
            framework, working_days=True, ceil=True
        )
