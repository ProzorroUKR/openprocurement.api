from logging import getLogger

from openprocurement.relocation.api.database import TransferCollection
from openprocurement.relocation.api.utils import extract_transfer_doc

LOGGER = getLogger("openprocurement.relocation.api")


def includeme(config):
    LOGGER.info("Init relocation.api plugin.")

    config.registry.mongodb.add_collection("transfers", TransferCollection)

    config.add_request_method(extract_transfer_doc, "transfer_doc", reify=True)
    config.scan("openprocurement.relocation.api.procedure.views")
