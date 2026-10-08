from datetime import datetime, timedelta

from openprocurement.api.constants import TZ, WORKING_DAYS_WITH_WORKING_WEEKENDS

# procurement method types served by the open package
ABOVE_THRESHOLD = "aboveThreshold"
ABOVE_THRESHOLD_UA = "aboveThresholdUA"
ABOVE_THRESHOLD_EU = "aboveThresholdEU"
ABOVE_THRESHOLD_UA_DEFENSE = "aboveThresholdUA.defense"
SIMPLE_DEFENSE = "simple.defense"
COMPETITIVE_ORDERING = "competitiveOrdering"
BELOW_THRESHOLD = "belowThreshold"
REQUEST_FOR_PROPOSAL = "requestForProposal"

OPEN_PROCUREMENT_METHOD_TYPES = [
    ABOVE_THRESHOLD,
    ABOVE_THRESHOLD_UA,
    ABOVE_THRESHOLD_EU,
    ABOVE_THRESHOLD_UA_DEFENSE,
    SIMPLE_DEFENSE,
    COMPETITIVE_ORDERING,
    BELOW_THRESHOLD,
    REQUEST_FOR_PROPOSAL,
]

# route name prefix of the resources shared by the open procedures
OPEN_ROUTE_PREFIX = "open"


# aboveThreshold
ABOVE_THRESHOLD_CLAIM_SUBMIT_TIME = timedelta(days=3)
ABOVE_THRESHOLD_TENDERING_EXTRA_PERIOD = timedelta(days=4)
ABOVE_THRESHOLD_PERIOD_END_REQUIRED_FROM = datetime(2016, 7, 16, tzinfo=TZ)
ABOVE_THRESHOLD_STATUS4ROLE = {
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

ABOVE_THRESHOLD_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": False,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": False,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}


# aboveThresholdUA
ABOVE_THRESHOLD_UA_CLAIM_SUBMIT_TIME = timedelta(days=10)
ABOVE_THRESHOLD_UA_TENDERING_EXTRA_PERIOD = timedelta(days=7)
ABOVE_THRESHOLD_UA_PERIOD_END_REQUIRED_FROM = datetime(2016, 7, 16, tzinfo=TZ)
ABOVE_THRESHOLD_UA_STATUS4ROLE = {
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

ABOVE_THRESHOLD_UA_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": False,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}


# aboveThresholdEU
ABOVE_THRESHOLD_EU_TENDERING_AUCTION = timedelta(days=35)
ABOVE_THRESHOLD_EU_QUESTIONS_STAND_STILL = timedelta(days=10)
ABOVE_THRESHOLD_EU_BID_UNSUCCESSFUL_FROM = datetime(2016, 10, 18, tzinfo=TZ)

ABOVE_THRESHOLD_EU_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": False,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}
ABOVE_THRESHOLD_EU_CLAIM_SUBMIT_TIME = timedelta(days=10)
ABOVE_THRESHOLD_EU_TENDERING_EXTRA_PERIOD = timedelta(days=7)


# aboveThresholdUA.defense
ABOVE_THRESHOLD_UA_DEFENSE_WORKING_DAYS = WORKING_DAYS_WITH_WORKING_WEEKENDS

ABOVE_THRESHOLD_UA_DEFENSE_CLAIM_SUBMIT_TIME = timedelta(days=3)
ABOVE_THRESHOLD_UA_DEFENSE_COMPLAINT_OLD_SUBMIT_TIME = timedelta(days=3)
ABOVE_THRESHOLD_UA_DEFENSE_COMPLAINT_OLD_SUBMIT_TIME_BEFORE = datetime(2016, 7, 5, tzinfo=TZ)
ABOVE_THRESHOLD_UA_DEFENSE_TENDERING_EXTRA_PERIOD = timedelta(days=2)

ABOVE_THRESHOLD_UA_DEFENSE_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": True,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": True,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": True,
    "qualificationComplainDuration": False,
}


# simple.defense
SIMPLE_DEFENSE_CLAIM_SUBMIT_TIME = timedelta(days=3)
SIMPLE_DEFENSE_COMPLAINT_OLD_SUBMIT_TIME = timedelta(days=3)
SIMPLE_DEFENSE_COMPLAINT_OLD_SUBMIT_TIME_BEFORE = datetime(2016, 7, 5, tzinfo=TZ)
SIMPLE_DEFENSE_TENDERING_EXTRA_PERIOD = timedelta(days=2)

SIMPLE_DEFENSE_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": True,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": True,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": True,
    "qualificationComplainDuration": False,
}


# competitiveOrdering
COMPETITIVE_ORDERING_CLAIM_SUBMIT_TIME = timedelta(days=3)
COMPETITIVE_ORDERING_TENDERING_EXTRA_PERIOD = timedelta(days=3)
COMPETITIVE_ORDERING_PERIOD_END_REQUIRED_FROM = datetime(2016, 7, 16, tzinfo=TZ)
COMPETITIVE_ORDERING_STATUS4ROLE = {
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

COMPETITIVE_ORDERING_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": [True, False],
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": False,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}

COMPETITIVE_ORDERING_SHORT_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": True,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": False,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}

COMPETITIVE_ORDERING_LONG_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": False,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": False,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}


# belowThreshold
BELOW_THRESHOLD_MIN_BIDS_NUMBER = 2
BELOW_THRESHOLD_STATUS4ROLE = {
    "complaint_owner": ["draft", "answered"],
    "tender_owner": ["claim"],
}
BELOW_THRESHOLD_TENDERING_EXTRA_PERIOD = timedelta(days=2)

BELOW_THRESHOLD_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": True,
    "minEnquiriesDuration": True,
    "enquiryPeriodRegulation": True,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}


# requestForProposal
REQUEST_FOR_PROPOSAL_MIN_BIDS_NUMBER = 2
REQUEST_FOR_PROPOSAL_STATUS4ROLE = {
    "complaint_owner": ["draft", "answered"],
    "tender_owner": ["claim"],
}
REQUEST_FOR_PROPOSAL_TENDERING_EXTRA_PERIOD = timedelta(days=4)

REQUEST_FOR_PROPOSAL_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": False,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": False,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": True,
}
