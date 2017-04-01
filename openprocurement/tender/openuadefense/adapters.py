# -*- coding: utf-8 -*-
from openprocurement.tender.openua.adapters import (
    TenderAboveThresholdUAConfigurator
)
from openprocurement.tender.openuadefense.models import Tender


class TenderAboveThresholdUADefConfigurator(TenderAboveThresholdUAConfigurator):
    """ AboveThresholdUA Defense Tender configuration adapter """

    name = "AboveThresholdUA Defense Tender configurator"
    model = Tender
