# -*- coding: utf-8 -*-
from logging import getLogger
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.tender.openuadefense.models import Tender, IAboveThresholdUADefTender
from openprocurement.tender.openuadefense.adapters import TenderAboveThresholdUADefConfigurator

LOGGER = getLogger("openprocurement.tender.openuadefense")


def includeme(config):
    LOGGER.info("Init tender.openuadefense plugin.")

    config.add_tender_procurementMethodType(Tender)
    config.scan("openprocurement.tender.openuadefense.views")
    config.scan("openprocurement.tender.openuadefense.procedure.views")
    config.scan("openprocurement.tender.openuadefense.subscribers")
    config.registry.registerAdapter(
        TenderAboveThresholdUADefConfigurator, (IAboveThresholdUADefTender, IRequest), IContentConfigurator
    )
