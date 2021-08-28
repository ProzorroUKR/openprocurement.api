# -*- coding: utf-8 -*-
from logging import getLogger
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.tender.simpledefense.models import Tender, ISimpleDefTender
from openprocurement.tender.simpledefense.adapters import TenderSimpleDefConfigurator

LOGGER = getLogger("openprocurement.tender.simpledefense")


def includeme(config):
    LOGGER.info("Init tender.simpledefense plugin.")

    config.add_tender_procurementMethodType(Tender)
    config.scan("openprocurement.tender.simpledefense.views")
    config.scan("openprocurement.tender.simpledefense.procedure.views")
    config.scan("openprocurement.tender.simpledefense.subscribers")
    config.registry.registerAdapter(
        TenderSimpleDefConfigurator, (ISimpleDefTender, IRequest), IContentConfigurator
    )
