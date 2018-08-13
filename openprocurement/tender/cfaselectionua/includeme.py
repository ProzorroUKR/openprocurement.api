# -*- coding: utf-8 -*-
from openprocurement.tender.cfaselectionua.interfaces import ICFASelectionUATender
from openprocurement.tender.cfaselectionua.models.tender import Tender
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.tender.cfaselectionua.adapters import TenderBelowThersholdConfigurator


def includeme(config):
    config.add_tender_procurementMethodType(Tender)
    config.scan("openprocurement.tender.cfaselectionua.views")
    config.scan("openprocurement.tender.cfaselectionua.subscribers")
    config.registry.registerAdapter(TenderBelowThersholdConfigurator,
                                    (ICFASelectionUATender, IRequest),
                                    IContentConfigurator)
