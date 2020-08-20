# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.adapters import TenderAboveThresholdEUConfigurator
from openprocurement.tender.openua.adapters import TenderAboveThresholdUAConfigurator

from openprocurement.tender.competitivedialogue.constants import MINIMAL_NUMBER_OF_BIDS
from openprocurement.tender.competitivedialogue.models import (
    CompetitiveDialogEU,
    CompetitiveDialogUA,
    TenderStage2EU,
    TenderStage2UA,
)
from openprocurement.tender.openua.constants import TENDERING_DURATION as TENDERING_DURATION_UA
from openprocurement.tender.openeu.constants import TENDERING_DURATION as TENDERING_DURATION_EU
from openprocurement.tender.openeu.constants import PREQUALIFICATION_COMPLAINT_STAND_STILL


class TenderCDEUConfigurator(TenderAboveThresholdEUConfigurator):
    """ Competitive Dialogue EU Tender configuration adapter """

    name = "Competitive Dialogue EU Tender configurator"
    model = CompetitiveDialogEU

    # minimal number of bids to pass the auction
    minimal_number_of_bids = MINIMAL_NUMBER_OF_BIDS

    block_tender_complaint_status = model.block_tender_complaint_status
    block_complaint_status = model.block_complaint_status


class TenderCDUAConfigurator(TenderCDEUConfigurator):
    """ Competitive Dialogue UA Tender configuration adapter """

    name = "Competitive Dialogue UA Tender configurator"
    model = CompetitiveDialogUA

    # duration of tendering period. timedelta object.
    tendering_period_duration = TENDERING_DURATION_UA


class TenderCDEUStage2Configurator(TenderAboveThresholdEUConfigurator):
    """ Competitive Dialogue EU Stage 2 Tender configuration adapter """

    name = "Competitive Dialogue EU Stage 2 Tender configurator"
    model = TenderStage2EU


class TenderCDUAStage2Configurator(TenderAboveThresholdUAConfigurator):
    """ Competitive Dialogue UA Stage 2 Tender configuration adapter """

    name = "Competitive Dialogue UA Stage 2 Tender configurator"
    model = TenderStage2UA
