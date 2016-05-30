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
    LOGGER.info('init competitivedialogue plugin')
    config.scan("openprocurement.tender.competitivedialogue.views")
