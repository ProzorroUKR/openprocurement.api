from openprocurement.api.utils import update_logging_context, raise_operation_error, get_now, parse_date
from openprocurement.api.validation import (
    OPERATIONS,
    validate_json_data,
    _validate_accreditation_level,
    validate_data,
    validate_doc_accreditation_level_mode,
)
from openprocurement.framework.core.utils import get_framework_by_id, get_submission_by_id
from openprocurement.framework.core.design import submissions_active_by_framework_id_count_view


def validate_framework_accreditation_level_central(request, model):
    _validate_accreditation_level(request, model.central_accreditations, "framework", "creation")


def validate_framework_data(request, **kwargs):
    update_logging_context(request, {"framework_id": "__new__"})
    data = validate_json_data(request)
    model = request.framework_from_data(data, create=False)
    validate_framework_accreditation_level_central(request, model)
    data = validate_data(request, model, data=data)
    validate_doc_accreditation_level_mode(request, "frameworkType", "framework")
    return data


def validate_patch_framework_data(request, **kwargs):
    data = validate_json_data(request)
    return validate_data(request, type(request.framework), True, data)


def validate_framework_patch_status(request, allowed_statuses=["draft"]):
    framework_status = request.validated["framework"].status
    if request.authenticated_role != "Administrator" and framework_status not in allowed_statuses:
        raise_operation_error(request, "Can't update framework in current ({}) status".format(framework_status))


def validate_submission_data(request, **kwargs):
    update_logging_context(request, {"submission_id": "__new__"})
    data = validate_json_data(request)
    model = request.submission_from_data(data, create=False)
    data = validate_data(request, model, data=data)
    framework = get_framework_by_id(request.registry.db, data["frameworkID"])
    if not framework:
        raise_operation_error(
            request,
            "frameworkID must be one of exists frameworks",
        )
    request.validated["framework"] = framework
    return data


def validate_patch_submission_data(request, **kwargs):
    data = validate_json_data(request)
    data = validate_data(request, type(request.submission), True, data)
    submission = request.validated["submission"]
    framework_id = data.get("frameworkID", submission["frameworkID"])
    framework = get_framework_by_id(request.registry.db, framework_id)
    if not framework:
        raise_operation_error(
            request,
            "frameworkID must be one of exists frameworks",
        )
    request.validated["framework"] = framework
    return data


def validate_operation_submission_in_not_allowed_period(request, **kwargs):
    framework = request.validated["framework"]
    enquiryPeriod = framework.get("enquiryPeriod")
    operation = OPERATIONS.get(request.method)
    period = framework.get("period")
    if (
        not enquiryPeriod
        or "endDate" not in enquiryPeriod
        or not period
        or "endDate" not in period
    ):
        raise_operation_error(
            request,
            "Submission cannot be {} without framework enquiryPeriod or period".format(operation)
        )
    enquiryPeriod_endDate = parse_date(enquiryPeriod["endDate"])
    period_endDate = parse_date(period["endDate"])
    now = get_now()

    if now < enquiryPeriod_endDate or now > period_endDate:
        raise_operation_error(
            request,
            "Submission can be {} only during the period: from ({}) to ({}).".format(
                operation, enquiryPeriod_endDate, period_endDate),
        )


def validate_submission_status(request, **kwargs):
    status_map = {
        "draft": ("draft", "active", "deleted"),
    }
    curr_status = request.validated["submission_src"]["status"]
    new_status = request.validated["data"].get("status", curr_status)

    available_statuses = status_map.get(curr_status, [])

    if new_status not in available_statuses:
        raise_operation_error(
            request,
            "Can't update submission from current ({}) to new ({}) status".format(
                curr_status, new_status
            )
        )


def validate_update_submission_in_not_allowed_status(request, **kwargs):
    status = request.validated["submission_src"]["status"]
    not_allowed_statuses = ("deleted", "active", "complete")

    if status in not_allowed_statuses:
        raise_operation_error(
            request,
            "Can't update submission in current ({}) status".format(status),
        )


def validate_document_operation_in_not_allowed_period(request, **kwargs):
    submission = request.validated["submission_src"]
    not_allowed_statuses = ("deleted", "active", "complete")
    if submission["status"] in not_allowed_statuses:
        raise_operation_error(
            request,
            "Can't {} document in current ({}) submission status".format(
                OPERATIONS.get(request.method), submission["status"],
            ),
        )


def validate_activate_submission(request, **kwargs):
    db = request.registry.db
    submission = request.validated["submission"]
    old_status = submission.status
    new_status = request.validated["data"].get("status", old_status)
    if new_status != "active" or old_status == new_status:
        return
    key = [submission.frameworkID, submission.tenderers[0].identifier.id]
    res = submissions_active_by_framework_id_count_view(db, key=key)
    if res:
        raise_operation_error(
            request,
            "Tenderer already have active submission for framework {}".format(submission.frameworkID)
        )

# Qualification validations

def validate_qualification_data(request, **kwargs):
    update_logging_context(request, {"qualification_id": "__new__"})
    data = validate_json_data(request)
    model = request.qualification_from_data(data, create=False)
    data = validate_data(request, model, data=data)
    submission = get_submission_by_id(request.registry.db, data["submissionID"])
    framework = get_framework_by_id(request.registry.db, data["frameworkID"])
    request.validated["submission"] = submission
    request.validated["framework"] = framework
    return data


def validate_patch_qualification_data(request, **kwargs):
    data = validate_json_data(request)
    return validate_data(request, type(request.qualification), True, data)


def validate_post_qualification_in_not_allowed_period(request, **kwargs):
    qualification = request.validated["qualification"]
    submission_status = request.validated["submission"]["status"]
    if submission_status != "active":
        raise_operation_error(
            request,
            "Can't post qualification to submission in current ({}) status".format(submission_status),
        )


def validate_update_qualification_in_not_allowed_status(request, **kwargs):
    qualification = request.validated["qualification_src"]
    not_allowed_statuses = ("unsuccessful", "active")
    if qualification["status"] in not_allowed_statuses:
        raise_operation_error(
            request,
            "Can't update qualification in current ({}) status".format(qualification["status"]),
        )


def validate_document_operation_in_not_allowed_status(request, **kwargs):
    qualification = request.validated["qualification_src"]
    not_allowed_statuses = ("unsuccessful", "active")
    if qualification["status"] in not_allowed_statuses:
        raise_operation_error(
            request,
            "Can't {} document in current ({}) qualification status".format(
                OPERATIONS.get(request.method), qualification["status"],
            ),
        )
