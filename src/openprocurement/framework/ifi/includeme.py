from logging import getLogger

LOGGER = getLogger("openprocurement.framework.ifi")


def includeme(config):
    LOGGER.info("Init framework.ifi plugin.")
    config.scan("openprocurement.framework.ifi.procedure.views")
