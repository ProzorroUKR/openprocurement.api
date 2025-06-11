from logging import getLogger

LOGGER = getLogger("openprocurement.contracting.contract")


def includeme(config):
    LOGGER.info("Init contracting.contract plugin.")
    config.scan("openprocurement.contracting.contract.procedure.views")
