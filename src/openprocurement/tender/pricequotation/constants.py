import re
from datetime import timedelta

PQ = "priceQuotation"
PQ_QUALIFICATION_DURATION = timedelta(days=2)
PQ_PROFILE_PATTERN = re.compile(r"^\d{6}-\d{8}-\d{6}-\d{8}")

PQ_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": True,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": True,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}
