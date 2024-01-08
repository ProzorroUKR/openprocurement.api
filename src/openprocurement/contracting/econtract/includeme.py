from logging import getLogger

LOGGER = getLogger("openprocurement.contracting.econtract")


def includeme(config):
    LOGGER.info("Init contracting.econtract plugin.")
    config.scan("openprocurement.contracting.econtract.procedure.views")
