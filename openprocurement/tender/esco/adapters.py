# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.adapters import TenderAboveThresholdEUConfigurator
from openprocurement.tender.esco.models import Tender


class TenderESCOConfigurator(TenderAboveThresholdEUConfigurator):
    """ AboveThresholdEU Tender configuration adapter """

    name = "escoEU Tender configurator"
    model = Tender
