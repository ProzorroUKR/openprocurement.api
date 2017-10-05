# -*- coding: utf-8 -*-
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.tender.esco.models import Tender, IESCOTender
from openprocurement.tender.esco.adapters import TenderESCOConfigurator


def includeme(config):
    config.add_tender_procurementMethodType(Tender)
    config.scan("openprocurement.tender.esco.views")
    config.scan("openprocurement.tender.esco.subscribers")
    config.registry.registerAdapter(TenderESCOConfigurator,
                                    (IESCOTender, IRequest),
                                    IContentConfigurator)
