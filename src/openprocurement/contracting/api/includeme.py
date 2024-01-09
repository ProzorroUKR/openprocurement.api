from logging import getLogger

LOGGER = getLogger("openprocurement.contracting.api")


def includeme(config):
    LOGGER.info("Init contracting.api plugin.")
    config.scan("openprocurement.contracting.api.procedure.views")
