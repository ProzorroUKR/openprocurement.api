# -*- coding: utf-8 -*-
from datetime import timedelta

PROCEDURES = {
    "": ("", "centralizedProcurement"),
    "open": (
        "belowThreshold",
        "aboveThresholdUA",
        "aboveThresholdEU",
        "aboveThresholdUA.defense",
        "competitiveDialogueUA",
        "competitiveDialogueEU",
        "esco",
        "closeFrameworkAgreementUA",
    ),
    "selective": ("priceQuotation",),
    "limited": ("reporting", "negotiation", "negotiation.quick"),
}

MULTI_YEAR_BUDGET_PROCEDURES = ("closeFrameworkAgreementUA",)
MULTI_YEAR_BUDGET_MAX_YEARS = 4

BREAKDOWN_OTHER = "other"
BREAKDOWN_TITLES = ["state", "crimea", "local", "own", "fund", "loan", BREAKDOWN_OTHER]

CENTRAL_PROCUREMENT_APPROVE_TIME = timedelta(days=20)
PROCURING_ENTITY_STANDSTILL = timedelta(days=2)

MILESTONE_APPROVAL_TITLE = u"Підготовка до проведення процедури"
MILESTONE_APPROVAL_DESCRIPTION = u"Узагальнення та аналіз отриманної інформації щодо проведення закупівель "\
                                 u"товарів, послуг (крім поточного ремонту) в інтересах замовників"
