from logging import getLogger

LOGGER = getLogger("openprocurement.tender.simpledefense")


def includeme(config):
    LOGGER.info("Init tender.simpledefense plugin.")
    config.scan("openprocurement.tender.simpledefense.procedure.views")
