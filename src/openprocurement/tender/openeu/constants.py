from datetime import datetime, timedelta

from openprocurement.api.constants import TZ

TENDERING_DAYS = 30
TENDERING_DURATION = timedelta(days=TENDERING_DAYS)
TENDERING_AUCTION = timedelta(days=35)
QUESTIONS_STAND_STILL = timedelta(days=10)
BID_UNSUCCESSFUL_FROM = datetime(2016, 10, 18, tzinfo=TZ)
ABOVE_THRESHOLD_EU = "aboveThresholdEU"
EU_KINDS = ("authority", "central", "defense", "general", "social", "special")
