from datetime import datetime, timedelta

from isodate import parse_duration

from openprocurement.api.constants import TZ

CFA_UA_TENDERING_AUCTION = timedelta(days=35)

CFA_UA_BID_UNSUCCESSFUL_FROM = datetime(2016, 10, 18, tzinfo=TZ)
CFA_UA_MIN_BIDS_NUMBER = 3
CFA_UA_TENDERING_EXTRA_PERIOD = timedelta(days=7)
CFA_UA_CLARIFICATIONS_UNTIL_PERIOD = timedelta(days=5)
CFA_UA_MAX_AGREEMENT_PERIOD = parse_duration("P4Y")
CFA_UA = "closeFrameworkAgreementUA"

CFA_UA_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": False,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}

CFA_UA_LOTS_MIN_SIZE = 1
CFA_UA_LOTS_MAX_SIZE = 1
CFA_UA_CLAIM_SUBMIT_TIME = timedelta(days=10)
