# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
from openprocurement.api.constants import TZ

STAND_STILL_TIME = timedelta(days=4)
ENQUIRY_STAND_STILL_TIME = timedelta(days=2)
CLAIM_SUBMIT_TIME = timedelta(days=3)
COMPLAINT_SUBMIT_TIME = timedelta(days=2)
COMPLAINT_OLD_SUBMIT_TIME = timedelta(days=3)
COMPLAINT_OLD_SUBMIT_TIME_BEFORE = datetime(2016, 7, 5, tzinfo=TZ)
TENDER_PERIOD = timedelta(days=6)
ENQUIRY_PERIOD_TIME = timedelta(days=3)
TENDERING_EXTRA_PERIOD = timedelta(days=2)

CALCULATE_BUSINESS_DATE_FROM = datetime(2017, 9, 8, tzinfo=TZ)
