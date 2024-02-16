from logging import getLogger

LOGGER = getLogger("openprocurement.tender.limited")


def includeme(config):
    LOGGER.info("Init tender.limited.reporting plugin.")
    config.scan("openprocurement.tender.limited.procedure.views")


def includeme_negotiation(config):
    LOGGER.info("Init tender.limited.negotiation plugin.")
    config.scan("openprocurement.tender.limited.procedure.views")


def includeme_negotiation_quick(config):
    LOGGER.info("Init tender.limited.negotiation.quick plugin.")
    config.scan("openprocurement.tender.limited.procedure.views")
