from datetime import timedelta

BELOW_THRESHOLD = "belowThreshold"

MIN_BIDS_NUMBER = 2
STATUS4ROLE = {
    "complaint_owner": ["draft", "answered"],
    "tender_owner": ["claim"],
}
TENDERING_EXTRA_PERIOD = timedelta(days=2)

WORKING_DAYS_CONFIG = {
    "minTenderingDuration": True,
    "minEnquiriesDuration": True,
    "enquiryPeriodRegulation": True,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}
