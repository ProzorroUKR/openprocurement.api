from datetime import timedelta

from openprocurement.api.constants import FAST_CATALOGUE_FLOW_FRAMEWORK_IDS
from openprocurement.api.utils import (
    update_logging_context,
    raise_operation_error,
    get_now,
)
from openprocurement.api.validation import (
    OPERATIONS,
    validate_json_data,
    validate_data,
    validate_doc_accreditation_level_mode,
    _validate_accreditation_level,
    _validate_accreditation_level_kind,
)
from openprocurement.framework.core.utils import (
    get_framework_by_id,
    get_submission_by_id,
    get_agreement_by_id,
    calculate_framework_date,
)


def validate_framework_accreditation_level(request, model):
    _validate_accreditation_level(request, model.create_accreditations, "framework", "creation")


def validate_framework_accreditation_level_central(request, model):
    data = request.validated["json_data"]
    kind = data.get("procuringEntity", {}).get("kind", "")
    _validate_accreditation_level_kind(request, model.central_accreditations, kind, "framework", "creation")


def validate_framework_data(request, **kwargs):
    update_logging_context(request, {"framework_id": "__new__"})
    data = validate_json_data(request)
    model = request.framework_from_data(data, create=False)
    validate_framework_accreditation_level(request, model)
    validate_framework_accreditation_level_central(request, model)
    data = validate_data(request, model, data=data)
    validate_doc_accreditation_level_mode(request, "frameworkType", "framework")
    return data


def validate_patch_framework_data(request, **kwargs):
    data = validate_json_data(request)
    data = validate_data(request, type(request.framework), True, data)
    framework = request.validated["framework"]
    if framework.agreementID:
        agreement = get_agreement_by_id(request, framework.agreementID)
        if not agreement:
            raise_operation_error(
                request,
                "agreementID must be one of exists agreement",
            )

        model = request.agreement_from_data(agreement, create=False)
        request.validated["agreement"] = agreement = model(agreement)
        agreement.__parent__ = framework.__parent__
        request.validated["agreement_src"] = agreement.serialize("plain")
    return data


def validate_framework_patch_status_base(request, allowed_statuses=None):
    allowed_statuses = allowed_statuses or ("draft",)
    framework_status = request.validated["framework"].status
    if request.authenticated_role != "Administrator" and framework_status not in allowed_statuses:
        raise_operation_error(request, "Can't update framework in current ({}) status".format(framework_status))


def validate_framework_patch_status(request, **kwargs):
    allowed_statuses = ("draft", "active")
    validate_framework_patch_status_base(request, allowed_statuses)


def validate_submission_data(request, **kwargs):
    update_logging_context(request, {"submission_id": "__new__"})
    data = validate_json_data(request)
    framework = get_framework_by_id(request, data.get("frameworkID"))
    if not framework:
        raise_operation_error(
            request,
            "frameworkID must be one of exists frameworks",
        )
    data["submissionType"] = framework["frameworkType"]
    model = request.submission_from_data(data, create=False)
    data = validate_data(request, model, data=data)
    model = request.framework_from_data(framework, create=False)
    framework = model(framework)
    request.validated["framework_src"] = framework.serialize("plain")
    request.validated["framework"] = framework
    request.validated["framework_config"] = framework.get("config") or {}
    return data


def validate_patch_submission_data(request, **kwargs):
    data = validate_json_data(request)
    data = validate_data(request, type(request.submission), True, data)
    submission = request.validated["submission"]
    framework_id = data.get("frameworkID", submission["frameworkID"])
    framework = get_framework_by_id(request, framework_id)
    if not framework:
        raise_operation_error(
            request,
            "frameworkID must be one of exists frameworks",
        )
    model = request.framework_from_data(framework, create=False)
    framework = model(framework)
    request.validated["framework_src"] = framework.serialize("plain")
    request.validated["framework"] = framework
    request.validated["framework_config"] = framework.get("config") or {}
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
    enquiryPeriod_endDate = enquiryPeriod["endDate"]
    period_endDate = period["endDate"]
    now = get_now()

    if now < enquiryPeriod_endDate or now > period_endDate:
        raise_operation_error(
            request,
            "Submission can be {} only during the period: from ({}) to ({}).".format(
                operation, enquiryPeriod_endDate, period_endDate),
        )


def validate_post_submission_with_active_contract(request, **kwargs):
    framework = request.validated["framework"]
    agreement = get_agreement_by_id(request, framework.get("agreementID"))
    submission_identifier_id = request.validated["submission"].tenderers[0].identifier.id
    if not agreement:
        return
    submission_contract = None
    for contract in agreement["contracts"]:
        if contract["suppliers"][0]["identifier"]["id"] == submission_identifier_id:
            submission_contract = contract
            break

    if submission_contract and submission_contract["status"] in ("active", "suspended"):
        raise_operation_error(
            request,
            f"Can't add submission when contract in "
            f"agreement with same identifier.id in {submission_contract['status']} status"
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
    if submission["frameworkID"] in FAST_CATALOGUE_FLOW_FRAMEWORK_IDS:
        not_allowed_statuses = ("deleted")
    else:
        not_allowed_statuses = ("deleted", "complete")
    if submission["status"] in not_allowed_statuses:
        raise_operation_error(
            request,
            "Can't {} document in current ({}) submission status".format(
                OPERATIONS.get(request.method), submission["status"],
            ),
        )


def validate_activate_submission(request, **kwargs):
    submission = request.validated["submission"]
    old_status = submission.status
    new_status = request.validated["data"].get("status", old_status)
    if new_status != "active" or old_status == new_status:
        return

    res = request.registry.mongodb.submissions.count_active_submissions_by_framework_id(
        submission.frameworkID,
        submission.tenderers[0].identifier.id,
    )
    if res:
        raise_operation_error(
            request,
            "Tenderer already have active submission for framework {}".format(submission.frameworkID)
        )

    res = request.registry.mongodb.agreements.has_active_suspended_contracts(
        submission.frameworkID,
        submission.tenderers[0].identifier.id,
    )
    if res:
        raise_operation_error(
            request,
            "Tenderer can't activate submission with active/suspended contract in agreement for framework {}".format(
                submission['frameworkID'])
        )


# Qualification validations
def validate_qualification_data(request, **kwargs):
    update_logging_context(request, {"qualification_id": "__new__"})
    data = validate_json_data(request)
    model = request.qualification_from_data(data, create=False)
    data = validate_data(request, model, data=data)
    submission = get_submission_by_id(request, data["submissionID"])
    framework = get_framework_by_id(request, data["frameworkID"])
    request.validated["submission"] = submission
    request.validated["framework"] = framework
    return data


def validate_patch_qualification_data(request, **kwargs):
    data = validate_json_data(request)
    qualification = request.validated["qualification"]
    framework_id = qualification["frameworkID"]
    framework = get_framework_by_id(request, framework_id)
    if not framework:
        raise_operation_error(
            request,
            "frameworkID must be one of existing frameworks",
        )
    model = request.framework_from_data(framework, create=False)
    framework = model(framework)
    framework.__parent__ = qualification.__parent__
    request.validated["framework_src"] = framework.serialize("plain")
    request.validated["framework"] = framework
    request.validated["framework_config"] = framework.get("config") or {}
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


def validate_agreement_data(request, **kwargs):
    update_logging_context(request, {"agreement_id": "__new__"})
    data = validate_json_data(request)
    model = request.agreement_from_data(data, create=False)
    _validate_agreement_accreditation_level(request, model)
    if data.get("frameworkID"):
        framework = get_framework_by_id(request, data["frameworkID"])
        if not framework:
            raise_operation_error(
                request,
                "frameworkID must be one of exists frameworks",
            )
        request.validated["framework"] = framework
    return validate_data(request, model, data=data)


def validate_action_in_not_allowed_framework_status(obj_name):
    def validation(request, **kwargs):
        framework_status = request.validated["framework"].get("status", "")

        if framework_status != "active":
            raise_operation_error(
                request,
                f"Can't {OPERATIONS.get(request.method)} {obj_name} in current ({framework_status}) framework status",
            )
    return validation


def _validate_agreement_accreditation_level(request, model, **kwargs):
    levels = model.create_accreditations
    _validate_accreditation_level(request, levels, "agreement", "creation")


def validate_patch_agreement_data(request, **kwargs):
    data = validate_json_data(request)
    return validate_data(request, type(request.agreement), True, data)


def validate_patch_contract_data(request, **kwargs):
    data = validate_json_data(request)
    return validate_data(request, type(request.validated["contract"]), True, data)


def validate_milestone_data(request, **kwargs):
    update_logging_context(request, {"milestone_id": "__new__"})
    model = type(request.validated["contract"]).milestones.model_class
    return validate_data(request, model)


def validate_patch_milestone_data(request, **kwargs):
    model = type(request.validated["contract"]).milestones.model_class
    return validate_data(request, model, True)


def validate_qualification_period_duration(request, model, min_duration, max_duration):
    data = request.validated["data"]
    qualification_period = model(request.validated["data"]["qualificationPeriod"])
    start_date = qualification_period["startDate"]
    if qualification_period["startDate"] < get_now():
        start_date = get_now()

    qualification_period_min_end_date = calculate_framework_date(
        start_date,
        timedelta(days=min_duration),
        data
    )
    qualification_period_max_end_date = calculate_framework_date(
        start_date,
        timedelta(days=max_duration),
        data,
        ceil=True
    )
    if qualification_period_min_end_date > qualification_period["endDate"]:
        raise_operation_error(
            request,
            "qualificationPeriod must be at least "
            "{min_duration} full calendar days long".format(
                min_duration=min_duration
            )
        )
    if qualification_period_max_end_date < qualification_period["endDate"]:
        raise_operation_error(
            request,
            "qualificationPeriod must be less than "
            "{max_duration} full calendar days long".format(
                max_duration=max_duration
            )
        )


def validate_framework_document_operation_not_in_allowed_status(request, **kwargs):
    if request.validated["framework"].status not in ["draft", "active"]:
        raise_operation_error(
            request,
            "Can't {} document in current ({}) framework status".format(
                OPERATIONS.get(request.method), request.validated["framework"].status
            ),
        )


def validate_agreement_operation_not_in_allowed_status(request, **kwargs):
    obj_name = "object"
    if "documents" in request.path:
        obj_name = "document"
    if request.validated["agreement"].status != "active":
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} {obj_name} "
            f"in current ({request.validated['agreement'].status}) agreement status"
        )


def validate_contract_operation_not_in_allowed_status(request, **kwargs):
    obj_name = "object"
    if "documents" in request.path:
        obj_name = "document"
    if request.validated["contract"].status not in ("active", "suspended"):
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} {obj_name} "
            f"in current ({request.validated['contract'].status}) contract status"
        )


def validate_milestone_type(request, **kwargs):
    obj_name = "object"
    if "documents" in request.path:
        obj_name = "document"
    if request.validated["milestone"].type == "activation":
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} {obj_name} for 'activation' milestone"
        )


def validate_contract_suspended(request, **kwargs):
    milestone_type = request.validated["milestone"].type
    if request.validated["contract"].status == "suspended" and milestone_type != "activation":
        raise_operation_error(
            request,
            f"Can't add {milestone_type} milestone for contract in suspended status"
        )


def validate_patch_not_activation_milestone(request, **kwargs):
    milestone = request.context
    if milestone.type != "activation":
        raise_operation_error(
            request,
            f"Can't patch `{milestone.type}` milestone"
        )


def validate_action_in_milestone_status(request, **kwargs):
    obj_name = "milestone document" if "documents" in request.path else "milestone"
    status = request.validated["milestone"].status
    if status != "scheduled":
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} {obj_name} in current ({status}) status "
        )


def validate_patch_milestone_status(request, **kwargs):
    milestone = request.context
    curr_status = milestone.status
    new_status = request.validated["data"].get("status", curr_status)

    if curr_status == new_status:
        return

    if new_status != "met":
        raise_operation_error(
            request,
            f"Can't switch milestone status from `{curr_status}` to `{new_status}`"
        )

def validate_restricted_access(obj_name, owner_fields=None):
    owner_fields = owner_fields or {"owner"}
    def validator(request, **kwargs):
        obj = request.validated[obj_name]
        config = request.validated["%s_config" % obj_name]

        if request.authenticated_role == "Administrator":
            return

        if request.authenticated_role == "chronograph":
            return

        if config.get("restricted") is True:
            if not any(getattr(obj, field, None) == request.authenticated_userid for field in owner_fields):
                raise_operation_error(
                    request,
                    "Access restricted for {} object".format(obj_name)
                )
    return validator
