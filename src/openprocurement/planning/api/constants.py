# -*- coding: utf-8 -*-
from datetime import timedelta

from openprocurement.tender.belowthreshold.constants import BELOW_THRESHOLD
from openprocurement.tender.cfaua.constants import CFA_UA
from openprocurement.tender.competitivedialogue.constants import CD_UA_TYPE, CD_EU_TYPE
from openprocurement.tender.esco.constants import ESCO
from openprocurement.tender.limited.constants import REPORTING, NEGOTIATION, NEGOTIATION_QUICK
from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.openeu.constants import ABOVE_THRESHOLD_EU
from openprocurement.tender.openua.constants import ABOVE_THRESHOLD_UA
from openprocurement.tender.openuadefense.constants import ABOVE_THRESHOLD_UA_DEFENSE
from openprocurement.tender.pricequotation.constants import PQ
from openprocurement.tender.simpledefense.constants import SIMPLE_DEFENSE

PROCEDURES = {
    "": ("", "centralizedProcurement"),
    "open": (
        BELOW_THRESHOLD,
        ABOVE_THRESHOLD,
        ABOVE_THRESHOLD_UA,
        ABOVE_THRESHOLD_EU,
        ABOVE_THRESHOLD_UA_DEFENSE,
        SIMPLE_DEFENSE,
        CD_UA_TYPE,
        CD_EU_TYPE,
        ESCO,
        CFA_UA,
    ),
    "selective": (
        PQ,
    ),
    "limited": (
        REPORTING,
        NEGOTIATION,
        NEGOTIATION_QUICK,
    ),
}

MULTI_YEAR_BUDGET_PROCEDURES = (
    CFA_UA,
)
MULTI_YEAR_BUDGET_MAX_YEARS = 4

BREAKDOWN_OTHER = "other"
BREAKDOWN_TITLES = ["state", "crimea", "local", "own", "fund", "loan", BREAKDOWN_OTHER]

CENTRAL_PROCUREMENT_APPROVE_TIME = timedelta(days=20)
PROCURING_ENTITY_STANDSTILL = timedelta(days=2)

MILESTONE_APPROVAL_TITLE = "Підготовка до проведення процедури"
MILESTONE_APPROVAL_DESCRIPTION = "Узагальнення та аналіз отриманної інформації щодо проведення закупівель "\
                                 "товарів, послуг (крім поточного ремонту) в інтересах замовників"
