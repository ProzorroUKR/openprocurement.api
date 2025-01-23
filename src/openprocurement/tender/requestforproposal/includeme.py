from logging import getLogger

LOGGER = getLogger("openprocurement.tender.requestforproposal")


def includeme(config):
    LOGGER.info("Init tender.requestforproposal plugin.")
    config.scan("openprocurement.tender.requestforproposal.procedure.views")
