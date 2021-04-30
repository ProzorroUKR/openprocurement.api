# -*- coding: utf-8 -*-
import os
from logging import getLogger
from openprocurement.api.interfaces import IContentConfigurator
from pyramid.interfaces import IRequest
from openprocurement.tender.cfaua.adapters.configurator import CloseFrameworkAgreementUAConfigurator
from openprocurement.tender.cfaua.interfaces import ICloseFrameworkAgreementUA
from openprocurement.tender.cfaua.models.tender import CloseFrameworkAgreementUA

LOGGER = getLogger("openprocurement.tender.cfaua")


def includeme(config):
    LOGGER.info("Init tender.cfaua plugin.")

    config.add_tender_procurementMethodType(CloseFrameworkAgreementUA)
    config.scan("openprocurement.tender.cfaua.views")
    config.scan("openprocurement.tender.cfaua.procedure.views")
    config.scan("openprocurement.tender.cfaua.subscribers")
    config.registry.registerAdapter(
        CloseFrameworkAgreementUAConfigurator, (ICloseFrameworkAgreementUA, IRequest), IContentConfigurator
    )
