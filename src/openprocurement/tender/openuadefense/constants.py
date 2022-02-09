# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
from openprocurement.api.constants import TZ

import standards

WORKING_DAYS = {}
HOLIDAYS = standards.load("calendars/workdays_off.json")
WORKING_WEEKENDS = standards.load("calendars/weekends_on.json")
for date_str in HOLIDAYS:
    WORKING_DAYS[date_str] = True
for date_str in WORKING_WEEKENDS:
    WORKING_DAYS[date_str] = False

TENDERING_DAYS = 6
TENDERING_DURATION = timedelta(days=TENDERING_DAYS)
STAND_STILL_TIME = timedelta(days=4)
ENQUIRY_STAND_STILL_TIME = timedelta(days=2)
CLAIM_SUBMIT_TIME = timedelta(days=3)
COMPLAINT_SUBMIT_TIME = timedelta(days=2)
COMPLAINT_OLD_SUBMIT_TIME = timedelta(days=3)
COMPLAINT_OLD_SUBMIT_TIME_BEFORE = datetime(2016, 7, 5, tzinfo=TZ)
ENQUIRY_PERIOD_TIME = timedelta(days=3)
TENDERING_EXTRA_PERIOD = timedelta(days=2)
ABOVE_THRESHOLD_UA_DEFENSE = "aboveThresholdUA.defense"
DEFENSE_KINDS = ("authority", "central", "defense", "general", "social", "special")
