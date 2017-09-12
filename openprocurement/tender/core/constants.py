# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from openprocurement.api.constants import TZ, CPV_ITEMS_CLASS_FROM


BIDDER_TIME = timedelta(minutes=6)
SERVICE_TIME = timedelta(minutes=9)
AUCTION_STAND_STILL_TIME = timedelta(minutes=15)
CANT_DELETE_PERIOD_START_DATE_FROM = datetime(2016, 8, 30, tzinfo=TZ)
COMPLAINT_STAND_STILL_TIME = timedelta(days=3)
BID_LOTVALUES_VALIDATION_FROM = datetime(2016, 10, 24, tzinfo=TZ)
ITEMS_LOCATION_VALIDATION_FROM = datetime(2016, 11, 22, tzinfo=TZ)
