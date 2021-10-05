# -*- coding: utf-8 -*-
from logging import getLogger
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.tender.limited.models import (
    ReportingTender,
    NegotiationTender,
    NegotiationQuickTender,
    IReportingTender,
    INegotiationTender,
    INegotiationQuickTender,
)
from openprocurement.tender.limited.adapters import (
    TenderReportingConfigurator,
    TenderNegotiationConfigurator,
    TenderNegotiationQuickConfigurator,
)

LOGGER = getLogger("openprocurement.tender.limited")


def includeme(config):
    LOGGER.info("Init tender.limited.reporting plugin.")
    config.add_tender_procurementMethodType(ReportingTender)
    config.scan("openprocurement.tender.limited.views")
    config.scan("openprocurement.tender.limited.procedure.views")
    config.scan("openprocurement.tender.limited.subscribers")
    config.registry.registerAdapter(TenderReportingConfigurator, (IReportingTender, IRequest), IContentConfigurator)


def includeme_negotiation(config):
    LOGGER.info("Init tender.limited.negotiation plugin.")
    config.add_tender_procurementMethodType(NegotiationTender)
    config.scan("openprocurement.tender.limited.views")
    config.scan("openprocurement.tender.limited.procedure.views")
    config.scan("openprocurement.tender.limited.subscribers")
    config.registry.registerAdapter(TenderNegotiationConfigurator, (INegotiationTender, IRequest), IContentConfigurator)


def includeme_negotiation_quick(config):
    LOGGER.info("Init tender.limited.negotiation.quick plugin.")
    config.add_tender_procurementMethodType(NegotiationQuickTender)
    config.scan("openprocurement.tender.limited.views")
    config.scan("openprocurement.tender.limited.procedure.views")
    config.scan("openprocurement.tender.limited.subscribers")
    config.registry.registerAdapter(
        TenderNegotiationQuickConfigurator, (INegotiationQuickTender, IRequest), IContentConfigurator
    )
