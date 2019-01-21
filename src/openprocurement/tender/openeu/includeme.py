# -*- coding: utf-8 -*-
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.tender.openeu.models import Tender, IAboveThresholdEUTender
from openprocurement.tender.openeu.adapters import TenderAboveThresholdEUConfigurator


def includeme(config):
    config.add_tender_procurementMethodType(Tender)
    config.scan("openprocurement.tender.openeu.views")
    config.scan("openprocurement.tender.openeu.subscribers")
    config.registry.registerAdapter(TenderAboveThresholdEUConfigurator,
                                    (IAboveThresholdEUTender, IRequest),
                                    IContentConfigurator)
