from openprocurement.relocation.api.database import TransferCollection
from openprocurement.api.database import COLLECTION_CLASSES
from logging import getLogger


LOGGER = getLogger("openprocurement.relocation.api")


def includeme(config):
    from openprocurement.relocation.api.utils import extract_transfer_doc

    LOGGER.info("Init relocation.api plugin.")
    COLLECTION_CLASSES["transfers"] = TransferCollection

    config.add_request_method(extract_transfer_doc, "transfer_doc", reify=True)
    config.scan("openprocurement.relocation.api.procedure.views")
