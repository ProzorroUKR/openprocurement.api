# -*- coding: utf-8 -*-
import os
from logging import getLogger
from openprocurement.tender.cfaselectionua.interfaces import ICFASelectionUATender
from openprocurement.tender.cfaselectionua.models.tender import CFASelectionUATender
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.tender.cfaselectionua.adapters.configurator import TenderCfaSelectionUAConfigurator

LOGGER = getLogger("openprocurement.tender.cfaselectionua")


def includeme(config):
    LOGGER.info("Init tender.cfaselectionua plugin.")

    config.add_tender_procurementMethodType(CFASelectionUATender)
    config.scan("openprocurement.tender.cfaselectionua.views")
    config.scan("openprocurement.tender.cfaselectionua.procedure.views")
    config.scan("openprocurement.tender.cfaselectionua.subscribers")
    config.registry.registerAdapter(
        TenderCfaSelectionUAConfigurator, (ICFASelectionUATender, IRequest), IContentConfigurator
    )
