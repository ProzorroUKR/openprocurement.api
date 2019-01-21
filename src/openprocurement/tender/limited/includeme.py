# -*- coding: utf-8 -*-
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.tender.limited.models import (
    ReportingTender, NegotiationTender, NegotiationQuickTender,
    IReportingTender, INegotiationTender, INegotiationQuickTender
)
from openprocurement.tender.limited.adapters import (
    TenderReportingConfigurator, TenderNegotiationConfigurator,
    TenderNegotiationQuickConfigurator
)


def includeme(config):
    config.add_tender_procurementMethodType(ReportingTender)
    config.scan("openprocurement.tender.limited.views")
    config.scan("openprocurement.tender.limited.subscribers")
    config.registry.registerAdapter(TenderReportingConfigurator,
                                    (IReportingTender, IRequest),
                                    IContentConfigurator)


def includeme_negotiation(config):
    config.add_tender_procurementMethodType(NegotiationTender)
    config.scan("openprocurement.tender.limited.views")
    config.scan("openprocurement.tender.limited.subscribers")
    config.registry.registerAdapter(TenderNegotiationConfigurator,
                                    (INegotiationTender, IRequest),
                                    IContentConfigurator)


def includeme_negotiation_quick(config):
    config.add_tender_procurementMethodType(NegotiationQuickTender)
    config.scan("openprocurement.tender.limited.views")
    config.scan("openprocurement.tender.limited.subscribers")
    config.registry.registerAdapter(TenderNegotiationQuickConfigurator,
                                    (INegotiationQuickTender, IRequest),
                                    IContentConfigurator)
