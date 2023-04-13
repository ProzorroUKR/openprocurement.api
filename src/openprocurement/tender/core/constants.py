# -*- coding: utf-8 -*-
from decimal import Decimal
from datetime import datetime, timedelta
from openprocurement.api.constants import TZ
from openprocurement.tender.belowthreshold.constants import BELOW_THRESHOLD
from openprocurement.tender.cfaua.constants import CFA_UA
from openprocurement.tender.competitivedialogue.constants import CD_UA_TYPE, CD_EU_TYPE
from openprocurement.tender.esco.constants import ESCO
from openprocurement.tender.limited.constants import REPORTING, NEGOTIATION, NEGOTIATION_QUICK
from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.openeu.constants import ABOVE_THRESHOLD_EU
from openprocurement.tender.openua.constants import ABOVE_THRESHOLD_UA
from openprocurement.tender.openuadefense.constants import ABOVE_THRESHOLD_UA_DEFENSE
from openprocurement.tender.pricequotation.constants import PQ as PRICEQUOTATION
from openprocurement.tender.simpledefense.constants import SIMPLE_DEFENSE

BIDDER_TIME = timedelta(minutes=6)
SERVICE_TIME = timedelta(minutes=9)
AUCTION_STAND_STILL_TIME = timedelta(minutes=15)
COMPLAINT_STAND_STILL_TIME = timedelta(days=3)

NORMALIZED_COMPLAINT_PERIOD_FROM = datetime(2016, 7, 20, tzinfo=TZ)
CANT_DELETE_PERIOD_START_DATE_FROM = datetime(2016, 9, 23, tzinfo=TZ)
BID_LOTVALUES_VALIDATION_FROM = datetime(2016, 10, 21, tzinfo=TZ)

AMOUNT_NET_COEF = Decimal("1.2")

FIRST_STAGE_PROCUREMENT_TYPES = {
    BELOW_THRESHOLD,
    CFA_UA,
    ESCO,
    CD_UA_TYPE,
    CD_EU_TYPE,
    REPORTING,
    NEGOTIATION,
    NEGOTIATION_QUICK,
    ABOVE_THRESHOLD_EU,
    ABOVE_THRESHOLD,
    ABOVE_THRESHOLD_UA,
    ABOVE_THRESHOLD_UA_DEFENSE,
    SIMPLE_DEFENSE,
    PRICEQUOTATION
}

CRITERION_LIFE_CYCLE_COST_IDS = [
    "CRITERION.OTHER.LIFE_CYCLE_COST.COST_OF_USE",
    "CRITERION.OTHER.LIFE_CYCLE_COST.MAINTENANCE_COST",
    "CRITERION.OTHER.LIFE_CYCLE_COST.END_OF_LIFE_COST",
    "CRITERION.OTHER.LIFE_CYCLE_COST.ECOLOGICAL_COST",
]

COMPLAINT_AMOUNT_RATE = 0.3 / 100
COMPLAINT_MIN_AMOUNT = 2000
COMPLAINT_MAX_AMOUNT = 85000
COMPLAINT_ENHANCED_AMOUNT_RATE = 0.6 / 100
COMPLAINT_ENHANCED_MIN_AMOUNT = 3000
COMPLAINT_ENHANCED_MAX_AMOUNT = 170000


ALP_MILESTONE_REASONS = (
    "найбільш економічно вигідна пропозиція є меншою на 40 або більше відсотків від середньоарифметичного значення "
    "ціни/приведеної ціни тендерних пропозицій інших учасників на початковому етапі аукціону",
    "найбільш економічно вигідна пропозиція є меншою на 30 або більше відсотків від наступної ціни/"
    "приведеної ціни тендерної пропозиції за результатами проведеного електронного аукціону"
)

AWARD_CRITERIA_LOWEST_COST = "lowestCost"
AWARD_CRITERIA_LIFE_CYCLE_COST = "lifeCycleCost"
AWARD_CRITERIA_RATED_CRITERIA = "ratedCriteria"
