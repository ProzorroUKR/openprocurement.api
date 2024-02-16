from logging import getLogger

LOGGER = getLogger("openprocurement.tender.open")


def includeme(config):
    LOGGER.info("Init tender.open plugin.")
    config.scan("openprocurement.tender.open.procedure.views")
