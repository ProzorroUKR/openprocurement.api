# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.adapters import TenderAboveThresholdEUConfigurator
from openprocurement.tender.esco.models import Tender


class TenderESCOConfigurator(TenderAboveThresholdEUConfigurator):
    """ AboveThresholdEU Tender configuration adapter """

    name = "esco Tender configurator"
    model = Tender

    # Param to configure award criteria - awards are generated from higher to lower by value.amount
    reverse_awarding_criteria = True
