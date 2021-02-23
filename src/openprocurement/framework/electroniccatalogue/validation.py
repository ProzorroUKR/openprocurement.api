from datetime import timedelta

from openprocurement.api.utils import raise_operation_error, get_now
from openprocurement.api.validation import OPERATIONS
from openprocurement.framework.core.validation import validate_framework_patch_status
from openprocurement.framework.electroniccatalogue.utils import calculate_framework_date

MIN_QUALIFICATION_DURATION = 30
MAX_QUALIFICATION_DURATION = 1095


def validate_qualification_period_duration(request, model):
    data = request.validated["data"]
    qualificationPeriod = model(request.validated["data"]["qualificationPeriod"])
    qualification_period_end_date = calculate_framework_date(qualificationPeriod.startDate,
                                                             timedelta(days=MIN_QUALIFICATION_DURATION), data)
    if qualification_period_end_date > qualificationPeriod.endDate:
        raise_operation_error(request,
                              "qualificationPeriod must be at least {min_duration} full calendar days long".format(
                                  min_duration=MIN_QUALIFICATION_DURATION))
    period = model(request.validated["data"]["period"])
    qualification_period_end_date = calculate_framework_date(period.startDate,
                                                             timedelta(days=MAX_QUALIFICATION_DURATION),
                                                             data, ceil=True)
    if qualification_period_end_date < qualificationPeriod.endDate:
        raise_operation_error(request,
                              "qualificationPeriod must be less than {max_duration} full calendar days long".format(
                                  max_duration=MAX_QUALIFICATION_DURATION))


def validate_ec_framework_patch_status(request, **kwargs):
    allowed_statuses = ("draft", "active")
    validate_framework_patch_status(request, allowed_statuses)


def validate_framework_document_operation_not_in_allowed_status(request, **kwargs):
    if request.validated["framework"].status not in ["draft", "active"]:
        raise_operation_error(
            request,
            "Can't {} document in current ({}) framework status".format(
                OPERATIONS.get(request.method), request.validated["framework"].status
            ),
        )


def validate_agreement_operation_not_in_allowed_status(request, **kwargs):
    if request.validated["agreement"].status != "active":
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document "
            f"in current ({request.validated['agreement'].status}) agreement status"
        )


def validate_contract_operation_not_in_allowed_status(request, **kwargs):
    if request.validated["contract"].status not in ("active", "banned"):
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document "
            f"in current ({request.validated['contract'].status}) contract status"
        )


def validate_milestone_type(request, **kwargs):
    if request.validated["milestone"].type == "activation":
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document for 'activation' milestone"
        )


def validate_contract_banned(request, **kwargs):
    milestone_type = request.validated["milestone"].type
    if request.validated["contract"].status == "banned" and milestone_type != "disqualification":
        raise_operation_error(
            request,
            f"Can't add {milestone_type} milestone for contract in banned status"
        )
