from datetime import datetime, timedelta

from openprocurement.api.constants import TZ

CLAIM_SUBMIT_TIME = timedelta(days=3)
COMPLAINT_OLD_SUBMIT_TIME = timedelta(days=3)
COMPLAINT_OLD_SUBMIT_TIME_BEFORE = datetime(2016, 7, 5, tzinfo=TZ)
TENDERING_EXTRA_PERIOD = timedelta(days=2)
SIMPLE_DEFENSE = "simple.defense"

WORKING_DAYS_CONFIG = {
    "minTenderingDuration": True,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": True,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": True,
    "qualificationComplainDuration": False,
}
