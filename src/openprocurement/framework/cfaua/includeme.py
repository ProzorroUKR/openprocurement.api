from logging import getLogger

LOGGER = getLogger("openprocurement.framework.cfaua")


def includeme(config):
    LOGGER.info("Init framework.cfaua plugin.")
    config.scan("openprocurement.framework.cfaua.procedure.views")
