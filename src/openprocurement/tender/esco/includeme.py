# -*- coding: utf-8 -*-
from logging import getLogger
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.tender.esco.models import Tender, IESCOTender
from openprocurement.tender.esco.adapters import TenderESCOConfigurator

LOGGER = getLogger("openprocurement.tender.esco")


def includeme(config):
    LOGGER.info("Init tender.esco plugin.")

    config.add_tender_procurementMethodType(Tender)
    config.scan("openprocurement.tender.esco.views")
    config.scan("openprocurement.tender.esco.procedure.views")
    config.scan("openprocurement.tender.esco.subscribers")
    config.registry.registerAdapter(TenderESCOConfigurator, (IESCOTender, IRequest), IContentConfigurator)
