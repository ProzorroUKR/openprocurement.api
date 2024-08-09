from openprocurement.api.constants import FAST_CATALOGUE_FLOW_FRAMEWORK_IDS
from openprocurement.api.context import get_now
from openprocurement.api.procedure.utils import is_item_owner
from openprocurement.api.utils import (
    get_agreement_by_id,
    get_framework_by_id,
    raise_operation_error,
    request_init_framework,
)
from openprocurement.api.validation import OPERATIONS
from openprocurement.framework.core.procedure.utils import (
    is_framework_owner,
    is_tender_owner,
)
from openprocurement.tender.core.procedure.utils import dt_from_iso


def validate_framework(request, item_name=None, **kwargs):
    data = request.validated["data"]
    previous_obj_framework_id = request.validated.get(item_name, {}).get("frameworkID")
    framework = get_framework_by_id(request, data.get("frameworkID", previous_obj_framework_id))
    request_init_framework(request, framework)


def validate_submission_framework(request, **kwargs):
    validate_framework(request, item_name="submission", **kwargs)


def validate_agreement_framework(request, **kwargs):
    validate_framework(request, item_name="agreement", **kwargs)


def validate_post_submission_with_active_contract(request, **kwargs):
    framework = request.validated["framework"]
    agreement = get_agreement_by_id(request, framework.get("agreementID"), raise_error=False)
    submission_identifier_id = request.validated["data"]["tenderers"][0]["identifier"]["id"]
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
            f"agreement with same identifier.id in {submission_contract['status']} status",
        )


def validate_activate_submission(request, **kwargs):
    submission = request.validated["submission"]
    old_status = submission["status"]
    new_status = request.validated["data"].get("status", old_status)
    if new_status != "active" or old_status == new_status:
        return

    res = request.registry.mongodb.submissions.count_active_submissions_by_framework_id(
        submission["frameworkID"],
        submission["tenderers"][0]["identifier"]["id"],
    )
    if res:
        raise_operation_error(
            request, f"Tenderer already have active submission for framework {submission['frameworkID']}"
        )

    res = request.registry.mongodb.agreements.has_active_suspended_contracts(
        submission["frameworkID"],
        submission["tenderers"][0]["identifier"]["id"],
    )
    if res:
        raise_operation_error(
            request,
            f"Tenderer can't activate submission with active/suspended contract in agreement "
            f"for framework {submission['frameworkID']}",
        )


def validate_framework_document_operation_not_in_allowed_status(request, **kwargs):
    if request.validated["framework"].get("status") not in ["draft", "active"]:
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document in current "
            f"({request.validated['framework']['status']}) framework status",
        )


def validate_framework_owner(item_name):
    def validator(request, **_):
        item = request.validated[item_name]
        if not is_framework_owner(request, item):
            raise_operation_error(request, "Forbidden", location="url", name="permission")

    return validator


def validate_tender_owner(item_name):
    def validator(request, **_):
        item = request.validated[item_name]
        if not is_tender_owner(request, item):
            raise_operation_error(request, "Forbidden", location="url", name="permission")

    return validator


def validate_operation_submission_in_not_allowed_period(request, **kwargs):
    framework = request.validated["framework"]
    operation = OPERATIONS.get(request.method)
    period = framework.get("period")
    if not period or "startDate" not in period or "endDate" not in period:
        raise_operation_error(request, "Submission cannot be {} without framework period".format(operation))
    period_startDate = dt_from_iso(period["startDate"])
    period_endDate = dt_from_iso(period["endDate"])
    now = get_now()

    if now < period_startDate or now > period_endDate:
        raise_operation_error(
            request,
            "Submission can be {} only during the period: from ({}) to ({}).".format(
                operation, period_startDate, period_endDate
            ),
        )


def validate_agreement_operation_not_in_allowed_status(request, **kwargs):
    obj_name = "object"
    if "documents" in request.path:
        obj_name = "document"
    if request.validated["agreement"]["status"] != "active":
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} {obj_name} "
            f"in current ({request.validated['agreement']['status']}) agreement status",
        )


def validate_contract_operation_not_in_allowed_status(request, **kwargs):
    obj_name = "object"
    if "documents" in request.path:
        obj_name = "document"
    if request.validated["contract"]["status"] not in ("active", "suspended"):
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} {obj_name} "
            f"in current ({request.validated['contract']['status']}) contract status",
        )


def validate_contract_suspended(request, **kwargs):
    milestone_type = request.validated["data"].get("type")
    if milestone_type and request.validated["contract"]["status"] == "suspended" and milestone_type != "activation":
        raise_operation_error(request, f"Can't add {milestone_type} milestone for contract in suspended status")


def validate_milestone_type(request, **kwargs):
    obj_name = "object"
    if "documents" in request.path:
        obj_name = "document"
    if request.validated["data"].get("type") == "activation":
        raise_operation_error(request, f"Can't {OPERATIONS.get(request.method)} {obj_name} for 'activation' milestone")


def validate_patch_not_activation_milestone(request, **kwargs):
    milestone = request.validated["milestone"]
    if milestone["type"] != "activation":
        raise_operation_error(request, f"Can't patch `{milestone['type']}` milestone")


def validate_action_in_milestone_status(request, **kwargs):
    obj_name = "milestone document" if "documents" in request.path else "milestone"
    status = request.validated["milestone"]["status"]
    if status != "scheduled":
        raise_operation_error(
            request, f"Can't {OPERATIONS.get(request.method)} {obj_name} in current ({status}) status "
        )


def validate_patch_milestone_status(request, **kwargs):
    milestone = request.validated["milestone"]
    curr_status = milestone["status"]
    new_status = request.validated["data"].get("status", curr_status)

    if curr_status == new_status:
        return

    if new_status != "met":
        raise_operation_error(request, f"Can't switch milestone status from `{curr_status}` to `{new_status}`")


def unless_administrator_or_chronograph(*validations):
    def decorated(request, **_):
        if request.authenticated_role not in ("chronograph", "Administrator"):
            for validation in validations:
                validation(request)

    return decorated


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
            if not any(obj.get(field, None) == request.authenticated_userid for field in owner_fields):
                raise_operation_error(request, "Access restricted for {} object".format(obj_name))

    return validator


def validate_document_operation_on_agreement_status(request, **kwargs):
    status = request.validated["agreement"]["status"]
    if status != "active":
        raise_operation_error(
            request, "Can't {} document in current ({}) agreement status".format(OPERATIONS.get(request.method), status)
        )


def validate_action_in_not_allowed_framework_status(obj_name):
    def validation(request, **kwargs):
        framework_status = request.validated["framework"].get("status", "")

        if framework_status != "active":
            raise_operation_error(
                request,
                f"Can't {OPERATIONS.get(request.method)} {obj_name} in current ({framework_status}) framework status",
            )

    return validation


def validate_update_submission_in_not_allowed_status(request, **kwargs):
    status = request.validated["submission_src"]["status"]
    not_allowed_statuses = ("deleted", "active", "complete")

    if status in not_allowed_statuses:
        raise_operation_error(
            request,
            f"Can't update submission in current ({status}) status",
        )


def validate_document_operation_in_not_allowed_period(request, **kwargs):
    submission = request.validated["submission_src"]
    if submission["frameworkID"] in FAST_CATALOGUE_FLOW_FRAMEWORK_IDS:
        not_allowed_statuses = "deleted"
    else:
        not_allowed_statuses = ("deleted", "complete")
    if submission["status"] in not_allowed_statuses:
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document in current ({submission['status']}) submission status",
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
            f"Can't update submission from current ({curr_status}) to new ({new_status}) status",
        )


def validate_update_qualification_in_not_allowed_status(request, **kwargs):
    qualification = request.validated["qualification_src"]
    not_allowed_statuses = ("unsuccessful", "active")
    if qualification["status"] in not_allowed_statuses:
        raise_operation_error(
            request,
            f"Can't update qualification in current ({qualification['status']}) status",
        )


def validate_document_operation_in_not_allowed_status(request, **kwargs):
    qualification = request.validated["qualification_src"]
    not_allowed_statuses = ("unsuccessful", "active")
    if qualification["status"] in not_allowed_statuses:
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document in current ({qualification['status']}) qualification status",
        )


def validate_download_submission_document(request, **_):
    if request.params.get("download"):
        document = request.validated["document"]
        submission = request.validated["submission"]
        if (
            document.get("confidentiality", "") == "buyerOnly"
            and not is_item_owner(request, submission)
            and not is_framework_owner(request, submission)
        ):
            raise_operation_error(request, "Document download forbidden.")
