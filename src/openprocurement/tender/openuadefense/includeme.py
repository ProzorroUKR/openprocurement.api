# -*- coding: utf-8 -*-
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.tender.openuadefense.models import (
    Tender, IAboveThresholdUADefTender
)
from openprocurement.tender.openuadefense.adapters import (
    TenderAboveThresholdUADefConfigurator
)


def includeme(config):
    config.add_tender_procurementMethodType(Tender)
    config.scan("openprocurement.tender.openuadefense.views")
    config.scan("openprocurement.tender.openuadefense.subscribers")
    config.registry.registerAdapter(TenderAboveThresholdUADefConfigurator,
                                    (IAboveThresholdUADefTender, IRequest),
                                    IContentConfigurator)
