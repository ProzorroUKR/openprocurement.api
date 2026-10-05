from logging import getLogger

from openprocurement.contracting.core.database import ContractCollection
from openprocurement.contracting.core.procedure.serializers.config import (
    ContractConfigSerializer,
)
from openprocurement.contracting.core.utils import (
    ContractTypePredicate,
    extract_contract_doc,
)

LOGGER = getLogger("openprocurement.contracting.core")


def includeme(config):
    LOGGER.info("Init contracting.core plugin.")

    config.registry.mongodb.add_collection("contracts", ContractCollection)
    config.add_request_method(extract_contract_doc, "contract_doc", reify=True)
    config.add_route_predicate("contractType", ContractTypePredicate)
    config.add_config_serializer("contract", ContractConfigSerializer)
    config.scan("openprocurement.contracting.core.procedure.views")
