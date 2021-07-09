# -*- coding: utf-8 -*-
from logging import getLogger
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.tender.openeu.models import Tender, IAboveThresholdEUTender
from openprocurement.tender.openeu.adapters import TenderAboveThresholdEUConfigurator

LOGGER = getLogger("openprocurement.tender.openeu")


def includeme(config):
    LOGGER.info("Init tender.openeu plugin.")

    config.add_tender_procurementMethodType(Tender)
    config.scan("openprocurement.tender.openeu.views")
    config.scan("openprocurement.tender.openeu.procedure.views")
    config.scan("openprocurement.tender.openeu.subscribers")
    config.registry.registerAdapter(
        TenderAboveThresholdEUConfigurator, (IAboveThresholdEUTender, IRequest), IContentConfigurator
    )
