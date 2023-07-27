from logging import getLogger

from openprocurement.contracting.econtract.procedure.models.contract import Contract

LOGGER = getLogger("openprocurement.contracting.econtract")


def includeme(config):
    LOGGER.info("Init contracting.econtract plugin.")
    config.add_contract_type(Contract)
    config.scan("openprocurement.contracting.econtract.procedure.views")
