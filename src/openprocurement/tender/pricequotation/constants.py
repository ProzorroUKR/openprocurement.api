import re
from datetime import timedelta

PQ = "priceQuotation"
TENDERING_DAYS = 2
TENDERING_DURATION = timedelta(days=TENDERING_DAYS)
QUALIFICATION_DURATION = timedelta(days=2)
PROFILE_PATTERN = re.compile(r"^\d{6}-\d{8}-\d{6}-\d{8}")
PQ_KINDS = ["general", "special", "defense", "other", "social", "authority"]
DEFAULT_TEMPLATE_KEY = "00000000-0"
