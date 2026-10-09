from logging import getLogger

LOGGER = getLogger("openprocurement.framework.arma")


def includeme(config):
    LOGGER.info("Init framework.arma plugin.")
    config.scan("openprocurement.framework.arma.procedure.views")
