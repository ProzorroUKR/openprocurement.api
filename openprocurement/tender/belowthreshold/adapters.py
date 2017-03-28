# -*- coding: utf-8 -*-
from openprocurement.tender.core.adapters import TenderConfigurator


class TenderBelowThersholdConfigurator(TenderConfigurator):
    """ BelowThreshold Tender configuration adapter """

    name = "BelowThreshold configurator"
