# -*- coding: utf-8 -*-
from openprocurement.tender.openuadefense.adapters import TenderAboveThresholdUADefConfigurator
from openprocurement.tender.simpledefense.models import Tender


class TenderSimpleDefConfigurator(TenderAboveThresholdUADefConfigurator):
    """ Simple Defense Tender configuration adapter """

    name = "Simple Defense Tender configurator"
    model = Tender
