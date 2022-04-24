from openprocurement.api.database import COLLECTION_CLASSES
from openprocurement.contracting.api.database import ContractCollection
from logging import getLogger

LOGGER = getLogger("openprocurement.contracting.api")


def includeme(config):
    from openprocurement.contracting.api.utils import contract_from_data, extract_contract

    LOGGER.info("Init contracting.api plugin.")
    COLLECTION_CLASSES["contracts"] = ContractCollection
    config.add_request_method(extract_contract, "contract", reify=True)
    config.add_request_method(contract_from_data)
    config.scan("openprocurement.contracting.api.views")
