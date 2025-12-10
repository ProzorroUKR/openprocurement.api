import re
from datetime import timedelta

PQ = "priceQuotation"
QUALIFICATION_DURATION = timedelta(days=2)
PROFILE_PATTERN = re.compile(r"^\d{6}-\d{8}-\d{6}-\d{8}")

WORKING_DAYS_CONFIG = {
    "minTenderingDuration": True,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": True,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}
