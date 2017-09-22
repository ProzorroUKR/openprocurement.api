# -*- coding: utf-8 -*-
from logging import getLogger
from pkg_resources import get_distribution
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.tender.competitivedialogue.models import Tender
from openprocurement.tender.competitivedialogue.models import (
    ICDEUTender, ICDUATender, ICDEUStage2Tender, ICDUAStage2Tender
)
from openprocurement.tender.competitivedialogue.adapters import (
    TenderCDEUConfigurator, TenderCDUAConfigurator,
    TenderCDEUStage2Configurator, TenderCDUAStage2Configurator
)

PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def includeme(config):
    """
    Entry point to module
    :param config: Pyramid server configuration
    :return:
    """
    from openprocurement.tender.competitivedialogue.models import (
        CompetitiveDialogUA, CompetitiveDialogEU,
        TenderStage2EU, TenderStage2UA
    )
    LOGGER.info('init competitivedialogue plugin')
    # add two types of Competitive Dialogue
    config.add_tender_procurementMethodType(CompetitiveDialogUA)
    config.add_tender_procurementMethodType(CompetitiveDialogEU)
    config.add_tender_procurementMethodType(TenderStage2EU)
    config.add_tender_procurementMethodType(TenderStage2UA)
    config.scan("openprocurement.tender.competitivedialogue.views.stage1")
    config.scan("openprocurement.tender.competitivedialogue.views.stage2")
    config.scan("openprocurement.tender.competitivedialogue.subscribers")
    config.registry.registerAdapter(TenderCDEUConfigurator,
                                    (ICDEUTender, IRequest),
                                    IContentConfigurator)
    config.registry.registerAdapter(TenderCDUAConfigurator,
                                    (ICDUATender, IRequest),
                                    IContentConfigurator)
    config.registry.registerAdapter(TenderCDEUStage2Configurator,
                                    (ICDEUStage2Tender, IRequest),
                                    IContentConfigurator)
    config.registry.registerAdapter(TenderCDUAStage2Configurator,
                                    (ICDUAStage2Tender, IRequest),
                                    IContentConfigurator)
