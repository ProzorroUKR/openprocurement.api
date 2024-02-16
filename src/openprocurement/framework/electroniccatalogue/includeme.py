from logging import getLogger

LOGGER = getLogger("openprocurement.framework.electroniccatalogue")


def includeme(config):
    LOGGER.info("Init framework.electroniccatalogue plugin.")
    config.scan("openprocurement.framework.electroniccatalogue.procedure.views")
