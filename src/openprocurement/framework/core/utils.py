from datetime import timedelta

from functools import (
    partial,
    wraps,
)
from logging import getLogger

from cornice.resource import resource
from dateorro import (
    calc_datetime,
    calc_normalized_datetime,
    calc_working_datetime,
)
from jsonpointer import resolve_pointer
from pyramid.compat import decode_path_info
from pyramid.exceptions import URLDecodeError

from openprocurement.api.constants import (
    WORKING_DAYS,
    FRAMEWORK_ENQUIRY_PERIOD_OFF_FROM,
)
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
    ACCELERATOR_RE,
    generate_id,
    get_first_revision_date,
)
from openprocurement.framework.core.traversal import (
    framework_factory,
    submission_factory,
    qualification_factory,
    agreement_factory,
    contract_factory,
)

LOGGER = getLogger("openprocurement.framework.core")
ENQUIRY_PERIOD_DURATION = 10
SUBMISSION_STAND_STILL_DURATION = 30
DAYS_TO_UNSUCCESSFUL_STATUS = 20
MILESTONE_CONTRACT_STATUSES = {
    "ban": "suspended",
    "terminated": "terminated",
}

frameworksresource = partial(resource, error_handler=error_handler, factory=framework_factory)
submissionsresource = partial(resource, error_handler=error_handler, factory=submission_factory)
qualificationsresource = partial(resource, error_handler=error_handler, factory=qualification_factory)
agreementsresource = partial(resource, error_handler=error_handler, factory=agreement_factory)
contractresource = partial(resource, error_handler=error_handler, factory=contract_factory)


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
    if len(parts) < 4 or parts[3] not in ("frameworks", "submissions", "qualifications", "agreements"):
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


def save_object(request, obj_name, with_test_mode=True, additional_obj_names="", insert=False):
    obj = request.validated[obj_name]

    if with_test_mode and obj.mode == "test":
        set_modetest_titles(obj)

    patch = get_revision_changes(obj.serialize("plain"), request.validated["%s_src" % obj_name])
    if patch:
        now = get_now()
        append_obj_revision(request, obj, patch, now)

        config = request.validated.get("%s_config" % obj_name)
        if config:
            obj["config"] = config

        old_date_modified = obj.dateModified
        modified = getattr(obj, "modified", True)

        for i in additional_obj_names:
            if i in request.validated:
                request.validated[i].dateModified = now

        with handle_store_exceptions(request):
            collection = getattr(request.registry.mongodb, f"{obj_name}s")
            collection.save(obj, insert=insert, modified=modified)
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


def save_framework(request, additional_obj_names="", insert=False):
    return save_object(request, "framework", additional_obj_names=additional_obj_names, insert=insert)


def save_submission(request, additional_obj_names="", insert=False):
    return save_object(
        request, "submission", with_test_mode=False,
        additional_obj_names=additional_obj_names, insert=insert
    )


def save_qualification(request, additional_obj_names="", insert=False):
    return save_object(
        request, "qualification", with_test_mode=False,
        additional_obj_names=additional_obj_names, insert=insert
    )


def save_agreement(request, additional_obj_names="", insert=False):
    return save_object(
        request, "agreement", with_test_mode=False,
        additional_obj_names=additional_obj_names, insert=insert
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


def apply_patch(request, obj_name, data=None, save=True, src=None, additional_obj_names=""):
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
            return save_func(request, additional_obj_names=additional_obj_names)


def append_obj_revision(request, obj, patch, date):
    status_changes = [p for p in patch if all(
        [
            p["path"].endswith("/status"),
            p["op"] == "replace"
        ]
    )]
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
    if submission_id:
        return request.registry.mongodb.submissions.get(submission_id)


def get_framework_by_id(request, framework_id):
    if framework_id:
        return request.registry.mongodb.frameworks.get(framework_id)


def get_agreement_by_id(request, agreement_id):
    if agreement_id:
        return request.registry.mongodb.agreements.get(agreement_id)


def set_agreement_ownership(item, request):
    item.owner_token = generate_id()


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
        return calc_working_datetime(date_obj, timedelta_obj, calendar=calendar)
    else:
        return calc_datetime(date_obj, timedelta_obj)


def calculate_framework_periods(request, model):
    framework = request.context
    data = request.validated["data"]

    enquiryPeriod_startDate = framework.enquiryPeriod and framework.enquiryPeriod.startDate or get_now()
    if get_first_revision_date(framework, default=get_now()) >= FRAMEWORK_ENQUIRY_PERIOD_OFF_FROM:
        enquiryPeriod_endDate = enquiryPeriod_startDate + timedelta(seconds=1)
    else:
        enquiryPeriod_endDate = (
            framework.enquiryPeriod
            and framework.enquiryPeriod.endDate
            or calculate_framework_date(
                enquiryPeriod_startDate,
                timedelta(days=ENQUIRY_PERIOD_DURATION),
                framework,
                working_days=True,
                ceil=True
            )
        )

    data["enquiryPeriod"] = {
        "startDate": enquiryPeriod_startDate,
        "endDate": enquiryPeriod_endDate,
    }

    qualification_endDate = model(data["qualificationPeriod"]).endDate
    period_startDate = framework.period and framework.period.startDate or get_now()
    period_endDate = calculate_framework_date(
        qualification_endDate,
        timedelta(days=-SUBMISSION_STAND_STILL_DURATION),
        framework,
    )
    data["period"] = {
        "startDate": period_startDate,
        "endDate": period_endDate,
    }

    data["qualificationPeriod"]["startDate"] = enquiryPeriod_endDate


def get_framework_unsuccessful_status_check_date(framework):
    if framework.period and framework.period.startDate:
        return calculate_framework_date(
            framework.period.startDate, timedelta(days=DAYS_TO_UNSUCCESSFUL_STATUS),
            framework, working_days=True, ceil=True
        )


def get_framework_number_of_submissions(request, framework):
    result = request.registry.mongodb.submissions.count_total_submissions_by_framework_id(framework.id)
    return result


def check_status(request):
    framework = request.validated["framework"]

    if framework.status == "active":
        if not framework.successful:
            unsuccessful_status_check = get_framework_unsuccessful_status_check_date(framework)
            if unsuccessful_status_check and unsuccessful_status_check < get_now():
                number_of_submissions = get_framework_number_of_submissions(request, framework)
                if number_of_submissions == 0:
                    LOGGER.info(
                        "Switched framework {} to {}".format(framework.id, "unsuccessful"),
                        extra=context_unpack(request, {"MESSAGE_ID": "switched_framework_unsuccessful"}),
                    )
                    framework.status = "unsuccessful"
                    return
                else:
                    framework.successful = True

        if framework.qualificationPeriod.endDate < get_now():
            LOGGER.info(
                "Switched framework {} to {}".format(framework.id, "complete"),
                extra=context_unpack(request, {"MESSAGE_ID": "switched_framework_complete"}),
            )
            framework.status = "complete"
            return


def check_agreement_status(request, now=None):
    if not now:
        now = get_now()
    if request.validated["agreement"].period.endDate < now:
        request.validated["agreement"].status = "terminated"
        for contract in request.validated["agreement"].contracts:
            for milestone in contract.milestones:
                if milestone.status == "scheduled":
                    milestone.status = "met" if milestone.dueDate and milestone.dueDate <= now else "notMet"
                    milestone.dateModified = now

            if contract.status == "active":
                contract.status = "terminated"
        return True


def check_contract_statuses(request, now=None):
    if not now:
        now = get_now()
    for contract in request.validated["agreement"].contracts:
        if contract.status == "suspended":
            for milestone in contract.milestones[::-1]:
                if milestone.type == "ban":
                    if milestone.dueDate <= now:
                        contract.status = "active"
                        milestone.status = "met"
                        milestone.dateModified = now
                    break


