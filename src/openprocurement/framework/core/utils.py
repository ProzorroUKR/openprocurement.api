from datetime import timedelta
from functools import wraps
from logging import getLogger

from dateorro import calc_datetime, calc_normalized_datetime, calc_working_datetime
from pyramid.compat import decode_path_info
from pyramid.exceptions import URLDecodeError

from openprocurement.api.constants import DST_AWARE_PERIODS_FROM, TZ, WORKING_DAYS
from openprocurement.api.utils import (
    error_handler,
    get_now,
    get_registry_object,
    update_logging_context,
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
    """Framework Route predicate."""

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
    """Submission Route predicate."""

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
    """Qualification Route predicate."""

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
    """Agreement route predicate."""

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


def generate_framework_pretty_id(request):
    ctime = get_now().date()
    index = request.registry.mongodb.get_next_sequence_value(f"framework_{ctime.isoformat()}")
    return "UA-F-{:04}-{:02}-{:02}-{:06}".format(
        ctime.year,
        ctime.month,
        ctime.day,
        index,
    )


def generate_agreement_id(request):
    ctime = get_now().date()
    index = request.registry.mongodb.get_next_sequence_value(f"agreement_{ctime.isoformat()}")
    return "UA-{:04}-{:02}-{:02}-{:06}".format(
        ctime.year,
        ctime.month,
        ctime.day,
        index,
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
            framework.period.startDate,
            timedelta(days=DAYS_TO_UNSUCCESSFUL_STATUS),
            framework,
            working_days=True,
            ceil=True,
        )
