# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta
from openprocurement.api.constants import TZ


STAND_STILL_TIME = timedelta(days=2)
# COMPLAINT_STAND_STILL_TIME = timedelta(days=3)
# BIDDER_TIME = timedelta(minutes=6)
# SERVICE_TIME = timedelta(minutes=9)
# AUCTION_STAND_STILL_TIME = timedelta(minutes=15)

# CANT_DELETE_PERIOD_START_DATE_FROM = datetime(2016, 8, 30, tzinfo=TZ)
# BID_LOTVALUES_VALIDATION_FROM = datetime(2016, 10, 24, tzinfo=TZ)
# CPV_ITEMS_CLASS_FROM = datetime(2017, 1, 1, tzinfo=TZ)
STATUS4ROLE = {
    'complaint_owner': ['draft', 'answered'],
    'reviewers': ['pending'],
    'tender_owner': ['claim'],
    }
MIN_BIDS_NUMBER = 2
