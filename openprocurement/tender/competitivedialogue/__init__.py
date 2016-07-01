from logging import getLogger
from pkg_resources import get_distribution

PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def includeme(config):
    """
    Entry point to module
    :param config: Pyramid server configuration
    :return:
    """
    from openprocurement.tender.competitivedialogue.models import (CompetitiveDialogUA, CompetitiveDialogEU,
                                                                   TenderStage2EU, TenderStage2UA)
    LOGGER.info('init competitivedialogue plugin')
    # add two types of Competitive Dialogue
    config.add_tender_procurementMethodType(CompetitiveDialogUA)
    config.add_tender_procurementMethodType(CompetitiveDialogEU)
    config.add_tender_procurementMethodType(TenderStage2EU)
    config.add_tender_procurementMethodType(TenderStage2UA)
    config.scan("openprocurement.tender.competitivedialogue.views")
