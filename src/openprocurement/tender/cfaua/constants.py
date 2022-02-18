from isodate import parse_duration
from datetime import timedelta, datetime
from openprocurement.api.constants import TZ


TENDERING_DAYS = 30
TENDERING_DURATION = timedelta(days=TENDERING_DAYS)
TENDERING_AUCTION = timedelta(days=35)

QUESTIONS_STAND_STILL = timedelta(days=10)  # it's ENQUIRY_PERIOD_TIME
ENQUIRY_PERIOD_TIME = timedelta(days=10)
ENQUIRY_STAND_STILL_TIME = timedelta(days=3)

PREQUALIFICATION_COMPLAINT_STAND_STILL = timedelta(days=5)
QUALIFICATION_COMPLAINT_STAND_STILL = timedelta(days=10)
COMPLAINT_STAND_STILL = timedelta(days=10)
BID_UNSUCCESSFUL_FROM = datetime(2016, 10, 18, tzinfo=TZ)
MIN_BIDS_NUMBER = 3
TENDERING_EXTRA_PERIOD = timedelta(days=7)
CLARIFICATIONS_UNTIL_PERIOD = timedelta(days=5)
MAX_AGREEMENT_PERIOD = parse_duration("P4Y")
CFA_UA = "closeFrameworkAgreementUA"
CFA_UA_KINDS = ("authority", "central", "defense", "general", "social", "special")
