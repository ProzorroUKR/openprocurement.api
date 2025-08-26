from datetime import datetime, timedelta

from openprocurement.api.constants import TZ

CLAIM_SUBMIT_TIME = timedelta(days=3)
TENDERING_EXTRA_PERIOD = timedelta(days=3)
PERIOD_END_REQUIRED_FROM = datetime(2016, 7, 16, tzinfo=TZ)
STATUS4ROLE = {
    "complaint_owner": [
        "draft",
        "answered",
        "claim",
        "pending",
        "accepted",
        "satisfied",
    ],
    "aboveThresholdReviewers": ["pending", "accepted", "stopping"],
    "tender_owner": ["claim", "pending", "accepted", "satisfied"],
}
POST_SUBMIT_TIME = timedelta(days=3)
UA_KINDS = ("authority", "central", "defense", "general", "social", "special")

COMPETITIVE_ORDERING = "competitiveOrdering"

WORKING_DAYS_CONFIG = {
    "minTenderingDuration": [True, False],
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": False,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}

SHORT_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": True,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": False,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}

LONG_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": False,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": False,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}
