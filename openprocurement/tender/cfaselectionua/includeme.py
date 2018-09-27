# -*- coding: utf-8 -*-
import os
import openprocurement.tender.cfaselectionua
from zope.configuration.xmlconfig import file as ZcmlFile
from openprocurement.tender.cfaselectionua.interfaces import ICFASelectionUATender
from openprocurement.tender.cfaselectionua.models.tender import CFASelectionUATender
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.tender.cfaselectionua.adapters.configurator import TenderCfaSelectionUAConfigurator


def includeme(config):
    config.add_tender_procurementMethodType(CFASelectionUATender)
    config.scan("openprocurement.tender.cfaselectionua.views")
    config.scan("openprocurement.tender.cfaselectionua.subscribers")
    config.registry.registerAdapter(TenderCfaSelectionUAConfigurator,
                                    (ICFASelectionUATender, IRequest),
                                    IContentConfigurator)
    ZcmlFile(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configure.zcml'),
        package=openprocurement.tender.cfaselectionua
    )
