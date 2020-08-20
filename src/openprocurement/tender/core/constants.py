# -*- coding: utf-8 -*-
from decimal import Decimal
from datetime import datetime, timedelta
from openprocurement.api.constants import TZ
from openprocurement.tender.competitivedialogue.constants import CD_UA_TYPE, CD_EU_TYPE
from openprocurement.tender.pricequotation.constants import PMT as PRICEQUOTATION


BIDDER_TIME = timedelta(minutes=6)
SERVICE_TIME = timedelta(minutes=9)
AUCTION_STAND_STILL_TIME = timedelta(minutes=15)
COMPLAINT_STAND_STILL_TIME = timedelta(days=3)

NORMALIZED_COMPLAINT_PERIOD_FROM = datetime(2016, 7, 20, tzinfo=TZ)
CANT_DELETE_PERIOD_START_DATE_FROM = datetime(2016, 9, 23, tzinfo=TZ)
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
    PRICEQUOTATION
}


COMPLAINT_AMOUNT_RATE = 0.3 / 100
COMPLAINT_MIN_AMOUNT = 2000
COMPLAINT_MAX_AMOUNT = 85000
COMPLAINT_ENHANCED_AMOUNT_RATE = 0.6 / 100
COMPLAINT_ENHANCED_MIN_AMOUNT = 3000
COMPLAINT_ENHANCED_MAX_AMOUNT = 170000


ALP_MILESTONE_REASONS = (
    u"найбільш економічно вигідна пропозиція є меншою на 40 або більше відсотків від середньоарифметичного значення "
    u"ціни/приведеної ціни тендерних пропозицій інших учасників на початковому етапі аукціону",
    u"найбільш економічно вигідна пропозиція є меншою на 30 або більше відсотків від наступної ціни/"
    u"приведеної ціни тендерної пропозиції за результатами проведеного електронного аукціону"
)
