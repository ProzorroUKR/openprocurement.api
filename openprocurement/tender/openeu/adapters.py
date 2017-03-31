# -*- coding: utf-8 -*-
from openprocurement.tender.core.adapters import TenderConfigurator
from openprocurement.tender.openeu.models import Tender
from openprocurement.tender.openua.constants import (
    TENDERING_EXTRA_PERIOD
)
from openprocurement.tender.openeu.constants import (
    TENDERING_DURATION, PREQUALIFICATION_COMPLAINT_STAND_STILL
)


class TenderAboveThresholdEUConfigurator(TenderConfigurator):
    """ AboveThresholdEU Tender configuration adapter """

    name = "AboveThresholdEU Tender configurator"
    model = Tender

    # duration of tendering period. timedelta object.
    tendering_period_duration = TENDERING_DURATION

    # duration of tender period extension. timedelta object
    tendering_period_extra = TENDERING_EXTRA_PERIOD

    # duration of pre-qualification stand-still period. timedelta object.
    prequalification_complaint_stand_still = PREQUALIFICATION_COMPLAINT_STAND_STILL

    block_tender_complaint_status = model.block_tender_complaint_status
    block_complaint_status = model.block_complaint_status
