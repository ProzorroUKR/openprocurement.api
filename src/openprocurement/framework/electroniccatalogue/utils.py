from datetime import timedelta

import standards
from dateorro import calc_normalized_datetime, calc_working_datetime, calc_datetime

from openprocurement.api.constants import WORKING_DAYS
from openprocurement.api.utils import get_now, context_unpack
from openprocurement.framework.core.design import (
    submissions_by_framework_id_total_view,
)
from openprocurement.framework.core.utils import (
    ENQUIRY_PERIOD_DURATION,
    SUBMISSION_STAND_STILL_DURATION,
    acceleratable, LOGGER
)

DAYS_TO_UNSUCCESSFUL_STATUS = 20
CONTRACT_BAN_DURATION = 90
AUTHORIZED_CPB = standards.load("organizations/authorized_cpb.json")


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
    enquiryPeriod_endDate = (framework.enquiryPeriod and framework.enquiryPeriod.endDate or calculate_framework_date(
        enquiryPeriod_startDate, timedelta(days=ENQUIRY_PERIOD_DURATION), framework, working_days=True, ceil=True)
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
    total_submission_results = submissions_by_framework_id_total_view(
        request.registry.db,
        startkey=[framework.id, None],
        endkey=[framework.id, {}]
    )
    if total_submission_results:
        return [e.value for e in total_submission_results][0]
    return 0


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


@acceleratable
def calculate_milestone_dueDate(date_obj, framework=None):
    date_obj = calc_normalized_datetime(date_obj, ceil=True)
    return calc_datetime(date_obj, CONTRACT_BAN_DURATION)


def create_milestone(milestone_type="activation", documents=[], framework=None):
    milestone_data = {
        "type": milestone_type,
        "dueDate": None if milestone_type != "ban" else calculate_milestone_dueDate(framework=framework),
        "documents": documents,
    }
    return milestone_data
