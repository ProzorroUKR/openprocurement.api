# -*- coding: utf-8 -*-
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.tender.belowthreshold.models import Tender, IBelowThresholdTender
from openprocurement.tender.belowthreshold.adapters import TenderBelowThersholdConfigurator



def includeme(config):
    config.add_tender_procurementMethodType(Tender)
    config.scan("openprocurement.tender.belowthreshold.views")
    config.scan("openprocurement.tender.belowthreshold.subscribers")
    config.registry.registerAdapter(TenderBelowThersholdConfigurator,
                                    (IBelowThresholdTender, IRequest),
                                    IContentConfigurator)
