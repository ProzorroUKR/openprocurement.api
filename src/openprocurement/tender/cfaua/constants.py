from datetime import datetime, timedelta

from isodate import parse_duration

from openprocurement.api.constants import TZ

TENDERING_AUCTION = timedelta(days=35)

BID_UNSUCCESSFUL_FROM = datetime(2016, 10, 18, tzinfo=TZ)
MIN_BIDS_NUMBER = 3
TENDERING_EXTRA_PERIOD = timedelta(days=7)
CLARIFICATIONS_UNTIL_PERIOD = timedelta(days=5)
MAX_AGREEMENT_PERIOD = parse_duration("P4Y")
CFA_UA = "closeFrameworkAgreementUA"

WORKING_DAYS_CONFIG = {
    "minTenderingDuration": False,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}
