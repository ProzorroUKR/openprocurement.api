from datetime import timedelta

import standards
from dateorro import calc_normalized_datetime, calc_working_datetime, calc_datetime

from openprocurement.api.constants import WORKING_DAYS
from openprocurement.api.utils import get_now, context_unpack
from openprocurement.framework.core.utils import (
    ENQUIRY_PERIOD_DURATION,
    SUBMISSION_STAND_STILL_DURATION,
    acceleratable, LOGGER
)

DAYS_TO_UNSUCCESSFUL_STATUS = 20
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


def check_status(request):
    framework = request.validated["framework"]
    number_of_submissions = request.validated["json_data"].get("numberOfSubmissions")

    if number_of_submissions is not None:
        unsuccessful_status_check = calculate_framework_date(framework.period.startDate, timedelta(days=DAYS_TO_UNSUCCESSFUL_STATUS), framework, working_days=True, ceil=True)
        if not number_of_submissions and unsuccessful_status_check < get_now():
            LOGGER.info(
                "Switched framework {} to {}".format(framework.id, "unsuccessful"),
                extra=context_unpack(request, {"MESSAGE_ID": "switched_framework_unsuccessful"}),
            )
            framework.status = "unsuccessful"
            return
    if framework.qualificationPeriod.endDate < get_now():
        LOGGER.info(
            "Switched framework {} to {}".format(framework.id, "complete"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_framework_complete"}),
        )
        framework.status = "complete"
        return
