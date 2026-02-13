from logging import getLogger

LOGGER = getLogger("openprocurement.tender.arma")


def includeme(config):
    LOGGER.info("Init tender.arma plugin.")
    config.scan("openprocurement.tender.arma.procedure.views")
