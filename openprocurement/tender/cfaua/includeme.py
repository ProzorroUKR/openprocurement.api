# -*- coding: utf-8 -*-
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.tender.cfaua.models import Tender, ICFASelectionUATender
from openprocurement.tender.cfaua.adapters import TenderBelowThersholdConfigurator



def includeme(config):
    config.add_tender_procurementMethodType(Tender)
    config.scan("openprocurement.tender.cfaua.views")
    config.scan("openprocurement.tender.cfaua.subscribers")
    config.registry.registerAdapter(TenderBelowThersholdConfigurator,
                                    (ICFASelectionUATender, IRequest),
                                    IContentConfigurator)
