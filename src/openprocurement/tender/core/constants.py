# -*- coding: utf-8 -*-
from decimal import Decimal
from datetime import datetime, timedelta
from openprocurement.api.constants import TZ, CPV_ITEMS_CLASS_FROM
from openprocurement.tender.competitivedialogue.constants import CD_UA_TYPE, CD_EU_TYPE

BIDDER_TIME = timedelta(minutes=6)
SERVICE_TIME = timedelta(minutes=9)
AUCTION_STAND_STILL_TIME = timedelta(minutes=15)
CANT_DELETE_PERIOD_START_DATE_FROM = datetime(2016, 9, 23, tzinfo=TZ)
COMPLAINT_STAND_STILL_TIME = timedelta(days=3)
BID_LOTVALUES_VALIDATION_FROM = datetime(2016, 10, 21, tzinfo=TZ)

AMOUNT_NET_COEF = Decimal("1.2")

FIRST_STAGE_PROCUREMENT_TYPES = {
    "belowThreshold",
    "closeFrameworkAgreementUA",
    "esco",
    CD_UA_TYPE,
    CD_EU_TYPE,
    "reporting",
    "negotiation",
    "negotiation.quick",
    "aboveThresholdEU",
    "aboveThresholdUA",
    "aboveThresholdUA.defense",
}
