from datetime import datetime, timedelta

from openprocurement.api.constants import TZ, WORKING_DAYS_WITH_WORKING_WEEKENDS

WORKING_DAYS = WORKING_DAYS_WITH_WORKING_WEEKENDS

CLAIM_SUBMIT_TIME = timedelta(days=3)
COMPLAINT_OLD_SUBMIT_TIME = timedelta(days=3)
COMPLAINT_OLD_SUBMIT_TIME_BEFORE = datetime(2016, 7, 5, tzinfo=TZ)
TENDERING_EXTRA_PERIOD = timedelta(days=2)
ABOVE_THRESHOLD_UA_DEFENSE = "aboveThresholdUA.defense"

WORKING_DAYS_CONFIG = {
    "minTenderingDuration": True,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": True,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": True,
    "qualificationComplainDuration": False,
}
# lots keep the openua tender period extension (the tender itself uses TENDERING_EXTRA_PERIOD)
LOT_TENDERING_EXTRA_PERIOD = timedelta(days=7)
