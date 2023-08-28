from logging import getLogger
from pkg_resources import iter_entry_points
from openprocurement.tender.core.utils import (
    ProcurementMethodTypePredicate,
    ComplaintTypePredicate,
)
from openprocurement.tender.core.procedure.utils import extract_complaint_type, extract_tender_doc
from openprocurement.api.database import COLLECTION_CLASSES
from openprocurement.tender.core.database import TenderCollection

LOGGER = getLogger("openprocurement.tender.core")


def includeme(config):
    LOGGER.info("Init tender.core plugin.")

    COLLECTION_CLASSES["tenders"] = TenderCollection
    config.add_request_method(extract_tender_doc, "tender_doc", reify=True)
    config.add_request_method(extract_complaint_type, "complaint_type", reify=True)

    # tender procurementMethodType plugins support
    config.registry.tender_procurementMethodTypes = {}
    config.add_route_predicate("procurementMethodType", ProcurementMethodTypePredicate)
    config.add_route_predicate("complaintType", ComplaintTypePredicate)
    config.scan("openprocurement.tender.core.procedure.views")
    config.scan("openprocurement.tender.core.subscribers")

    # search for plugins
    settings = config.get_settings()
    plugins = settings.get("plugins") and [plugin.strip() for plugin in settings["plugins"].split(",")]
    for entry_point in iter_entry_points("openprocurement.tender.core.plugins"):
        if not plugins or entry_point.name in plugins:
            plugin = entry_point.load()
            plugin(config)
