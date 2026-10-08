from datetime import timedelta

ESCO = "esco"

ESCO_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": False,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}
ESCO_TENDERING_EXTRA_PERIOD = timedelta(days=7)
