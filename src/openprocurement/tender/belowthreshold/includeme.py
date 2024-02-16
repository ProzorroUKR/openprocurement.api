from logging import getLogger

LOGGER = getLogger("openprocurement.tender.belowthreshold")


def includeme(config):
    LOGGER.info("Init tender.belowthreshold plugin.")
    config.scan("openprocurement.tender.belowthreshold.procedure.views")
