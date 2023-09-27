from logging import getLogger

from openprocurement.contracting.api.models import Contract

LOGGER = getLogger("openprocurement.contracting.api")


def includeme(config):
    LOGGER.info("Init contracting.api plugin.")
    config.add_contract_type(Contract)
    config.scan("openprocurement.contracting.api.views")
    config.scan("openprocurement.contracting.api.procedure.views")
