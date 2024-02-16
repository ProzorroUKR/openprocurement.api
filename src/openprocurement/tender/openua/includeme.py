from logging import getLogger

LOGGER = getLogger("openprocurement.tender.openua")


def includeme(config):
    LOGGER.info("Init tender.openua plugin.")
    config.scan("openprocurement.tender.openua.procedure.views")
