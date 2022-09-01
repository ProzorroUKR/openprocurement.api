# -*- coding: utf-8 -*-
from logging import getLogger
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.tender.open.models import Tender, IAboveThresholdTender
from openprocurement.tender.open.adapters import TenderAboveThresholdConfigurator

LOGGER = getLogger("openprocurement.tender.open")


def includeme(config):
    LOGGER.info("Init tender.open plugin.")

    config.add_tender_procurementMethodType(Tender)
    config.scan("openprocurement.tender.open.views")
    config.scan("openprocurement.tender.open.procedure.views")
    config.scan("openprocurement.tender.open.subscribers")
    config.registry.registerAdapter(
        TenderAboveThresholdConfigurator, (IAboveThresholdTender, IRequest), IContentConfigurator
    )
