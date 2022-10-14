from datetime import timedelta
from functools import partial

import standards
from cornice.resource import resource
from dateorro import calc_normalized_datetime, calc_working_datetime, calc_datetime

from openprocurement.api.constants import WORKING_DAYS, FRAMEWORK_ENQUIRY_PERIOD_OFF_FROM
from openprocurement.api.utils import get_now, context_unpack, error_handler, get_first_revision_date
from openprocurement.framework.core.utils import (
    ENQUIRY_PERIOD_DURATION,
    SUBMISSION_STAND_STILL_DURATION,
    acceleratable, LOGGER
)
from openprocurement.framework.electroniccatalogue.traversal import contract_factory

DAYS_TO_UNSUCCESSFUL_STATUS = 20
CONTRACT_BAN_DURATION = 90
AUTHORIZED_CPB = standards.load("organizations/authorized_cpb.json")
MILESTONE_CONTRACT_STATUSES = {"ban": "suspended", "terminated": "terminated"}

contractresource = partial(resource, factory=contract_factory, error_handler=error_handler)


@acceleratable
def calculate_framework_date(
        date_obj, timedelta_obj, framework=None, working_days=False, calendar=WORKING_DAYS, ceil=False):
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
        enquiryPeriod_endDate = (framework.enquiryPeriod and framework.enquiryPeriod.endDate
                                 or calculate_framework_date(enquiryPeriod_startDate,
                                                             timedelta(days=ENQUIRY_PERIOD_DURATION), framework,
                                                             working_days=True, ceil=True)
                                 )
    data["enquiryPeriod"] = {"startDate": enquiryPeriod_startDate, "endDate": enquiryPeriod_endDate}

    qualification_endDate = model(data["qualificationPeriod"]).endDate
    period_startDate = framework.period and framework.period.startDate or get_now()
    period_endDate = calculate_framework_date(
        qualification_endDate, timedelta(days=-SUBMISSION_STAND_STILL_DURATION), framework
    )
    data["period"] = {"startDate": period_startDate, "endDate": period_endDate}

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


def create_milestone_terminated():
    from openprocurement.framework.electroniccatalogue.models import Milestone
    return Milestone({"type": "terminated"})


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
                    if milestone.dueDate < now:
                        contract.status = "active"
                        milestone.status = "met"
                        milestone.dateModified = now
                    break
