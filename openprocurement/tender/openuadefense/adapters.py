# -*- coding: utf-8 -*-
from openprocurement.tender.openua.adapters import (
    TenderAboveThresholdUAConfigurator
)
from openprocurement.tender.openuadefense.models import Tender
from openprocurement.tender.openuadefense.constants import (
    TENDER_PERIOD, TENDERING_EXTRA_PERIOD,
    CLAIM_SUBMIT_TIME, COMPLAINT_SUBMIT_TIME
)


class TenderAboveThresholdUADefConfigurator(TenderAboveThresholdUAConfigurator):
    """ AboveThresholdUA Defense Tender configuration adapter """

    name = "AboveThresholdUA Defense Tender configurator"
    model = Tender

    # Duration of tendering period. timedelta object.
    tendering_period_duration = TENDER_PERIOD

    # Duration of tender period extension. timedelta object
    tendering_period_extra = TENDERING_EXTRA_PERIOD

    # Tender claims should be sumbitted not later then "tender_claim_submit_time" days before tendering period end. Timedelta object
    tender_claim_submit_time = CLAIM_SUBMIT_TIME

    # Tender complaints should be sumbitted not later then "tender_claim_submit_time" days before tendering period end. Timedelta object
    tender_complaint_submit_time = COMPLAINT_SUBMIT_TIME
