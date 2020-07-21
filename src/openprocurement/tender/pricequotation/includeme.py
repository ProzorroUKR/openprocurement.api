# -*- coding: utf-8 -*-
import os
import openprocurement.tender.pricequotation

from logging import getLogger
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.tender.pricequotation.interfaces import\
    IPriceQuotationTender
from openprocurement.tender.pricequotation.models.tender import\
    PriceQuotationTender
from openprocurement.tender.pricequotation.adapters import\
    PQTenderConfigurator


LOGGER = getLogger("openprocurement.tender.pricequotation")


def includeme(config):
    LOGGER.info("Init tender.pricequotation plugin.")
    config.add_tender_procurementMethodType(PriceQuotationTender)
    config.scan("openprocurement.tender.pricequotation.views")
    config.scan("openprocurement.tender.pricequotation.subscribers")
    config.registry.registerAdapter(
        PQTenderConfigurator,
        (IPriceQuotationTender, IRequest),
        IContentConfigurator
    )
