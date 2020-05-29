# -*- coding: utf-8 -*-
from datetime import timedelta


STAND_STILL_TIME = timedelta(days=2)

MIN_BIDS_NUMBER = 2
STATUS4ROLE = {
    "complaint_owner": ["draft", "answered"],
    "reviewers": ["pending"],
    "tender_owner": ["claim"]
}
