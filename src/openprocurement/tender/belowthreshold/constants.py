# -*- coding: utf-8 -*-
from datetime import timedelta

BELOW_THRESHOLD = "belowThreshold"
STAND_STILL_TIME = timedelta(days=2)
ENQUIRY_STAND_STILL_TIME = timedelta(days=1)

MIN_BIDS_NUMBER = 2
STATUS4ROLE = {
    "complaint_owner": ["draft", "answered"],
    "reviewers": ["pending"],
    "tender_owner": ["claim"]
}
BELOW_THRESHOLD_KINDS = ("authority", "central", "defense", "general", "other", "social", "special")
