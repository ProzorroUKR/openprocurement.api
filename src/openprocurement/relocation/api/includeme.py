from openprocurement.relocation.api.database import TransferCollection
from openprocurement.api.database import COLLECTION_CLASSES
from logging import getLogger

LOGGER = getLogger("openprocurement.relocation.api")


def includeme(config):
    from openprocurement.relocation.api.utils import transfer_from_data, extract_transfer

    LOGGER.info("Init relocation.api plugin.")
    COLLECTION_CLASSES["transfers"] = TransferCollection

    config.add_request_method(extract_transfer, "transfer", reify=True)
    config.add_request_method(transfer_from_data)
    config.scan("openprocurement.relocation.api.views")
