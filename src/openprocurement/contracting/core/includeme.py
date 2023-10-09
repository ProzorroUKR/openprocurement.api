from logging import getLogger
from pkg_resources import iter_entry_points

from openprocurement.api.database import COLLECTION_CLASSES
from openprocurement.contracting.core.database import ContractCollection
from openprocurement.contracting.core.utils import isContract, register_contract_type


LOGGER = getLogger("openprocurement.contracting.core")


def includeme(config):
    from openprocurement.contracting.core.utils import contract_from_data, extract_contract_doc, extract_contract

    LOGGER.info("Init contracting.core plugin.")
    COLLECTION_CLASSES["contracts"] = ContractCollection
    config.add_request_method(extract_contract_doc, "contract_doc", reify=True)
    config.add_request_method(extract_contract, "contract", reify=True)

    config.registry.contract_types = {}
    config.add_route_predicate("contractType", isContract)

    # config.add_request_method(contract_from_data)
    # config.add_directive("add_contract_type", register_contract_type)
    config.scan("openprocurement.contracting.core.procedure.views")

    settings = config.get_settings()
    plugins = settings.get("plugins") and [plugin.strip() for plugin in settings["plugins"].split(",")]
    for entry_point in iter_entry_points("openprocurement.contracting.core.plugins"):
        if not plugins or entry_point.name in plugins:
            plugin = entry_point.load()
            plugin(config)
