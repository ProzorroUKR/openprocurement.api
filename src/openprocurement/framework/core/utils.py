from functools import wraps
from logging import getLogger

from dateorro import calc_datetime

from openprocurement.api.constants import WORKING_DAYS
from openprocurement.api.utils import calculate_full_date, get_now
from openprocurement.api.validation import validate_json_data
from openprocurement.framework.cfaua.constants import CFA_UA
from openprocurement.framework.cfaua.procedure.utils import convert_agreement_type
from openprocurement.tender.core.utils import ACCELERATOR_RE

LOGGER = getLogger("openprocurement.framework.core")
ENQUIRY_PERIOD_DURATION = 10
SUBMISSION_STAND_STILL_DURATION = 30
ENQUIRY_STAND_STILL_TIME = 3
MILESTONE_CONTRACT_STATUSES = {
    "ban": "suspended",
    "terminated": "terminated",
}


class FrameworkTypePredicate:
    """Framework Route predicate."""

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return "frameworkType = {}".format(self.val)

    phash = text

    def __call__(self, context, request):
        if request.framework_doc is not None:
            return request.framework_doc.get("frameworkType", None) == self.val

        if request.method == "POST" and request.path.endswith("/frameworks"):
            data = validate_json_data(request)
            return data.get("frameworkType", "electronicCatalogue") == self.val

        return False


class SubmissionTypePredicate:
    """Submission Route predicate."""

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return "submissionType = {}".format(self.val)

    phash = text

    def __call__(self, context, request):
        if request.submission_doc is not None:
            return request.submission_doc.get("submissionType", None) == self.val

        if request.method == "POST" and request.path.endswith("/submissions"):
            data = validate_json_data(request)
            return data.get("submissionType", "electronicCatalogue") == self.val

        return False


class QualificationTypePredicate:
    """Qualification Route predicate."""

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return "qualificationType = {}".format(self.val)

    phash = text

    def __call__(self, context, request):
        if request.qualification_doc is not None:
            return request.qualification_doc.get("qualificationType", None) == self.val

        if request.method == "POST" and request.path.endswith("/qualifications"):
            data = validate_json_data(request)
            return data.get("qualificationType", "electronicCatalogue") == self.val

        return False


class AgreementTypePredicate:
    """Agreement route predicate."""

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return "agreementType = {}".format(self.val)

    phash = text

    def __call__(self, context, request):
        if request.agreement_doc is not None:
            agreement_type = request.agreement_doc.get("agreementType", None)
            agreement_type = convert_agreement_type(agreement_type)
            return agreement_type == self.val

        if request.method == "POST" and request.path.endswith("/agreements"):
            data = validate_json_data(request)
            agreement_type = data.get("agreementType", CFA_UA)
            agreement_type = convert_agreement_type(agreement_type)
            return agreement_type == self.val

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


def accelerated_framework(wrapped):
    @wraps(wrapped)
    def wrapper(date_obj, timedelta_obj, framework=None, **kwargs):
        accelerator = get_framework_accelerator(framework)
        if accelerator:
            return calc_datetime(date_obj, timedelta_obj, accelerator=accelerator)
        return wrapped(date_obj, timedelta_obj, **kwargs)

    return wrapper


@accelerated_framework
def calculate_framework_full_date(
    date_obj,
    timedelta_obj,
    working_days=False,
    calendar=WORKING_DAYS,
    ceil=False,
):
    return calculate_full_date(date_obj, timedelta_obj, working_days=working_days, calendar=calendar, ceil=ceil)
