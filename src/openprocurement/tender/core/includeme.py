from logging import getLogger
from pkg_resources import iter_entry_points
from pyramid.interfaces import IRequest
from openprocurement.tender.core.utils import (
    resolve_tender_model,
    extract_tender_doc,
    extract_tender,
    extract_complaint_type,
    isTender,
    isComplaint,
    register_tender_procurementMethodType,
    tender_from_data,
    SubscribersPicker,
)
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.api.database import COLLECTION_CLASSES
from openprocurement.tender.core.database import TenderCollection
from openprocurement.tender.core.models import ITender
from openprocurement.tender.core.adapters import TenderConfigurator

LOGGER = getLogger("openprocurement.tender.core")


def includeme(config):
    LOGGER.info("Init tender.core plugin.")

    COLLECTION_CLASSES["tenders"] = TenderCollection
    config.add_request_method(resolve_tender_model, "tender_model", reify=True)
    config.add_request_method(extract_tender_doc, "tender_doc", reify=True)
    config.add_request_method(extract_tender, "tender", reify=True)
    config.add_request_method(extract_complaint_type, "complaint_type", reify=True)

    # tender procurementMethodType plugins support
    config.registry.tender_procurementMethodTypes = {}
    config.add_route_predicate("procurementMethodType", isTender)
    config.add_route_predicate("complaintType", isComplaint)
    config.add_subscriber_predicate("procurementMethodType", SubscribersPicker)
    config.add_request_method(tender_from_data)
    config.add_directive("add_tender_procurementMethodType", register_tender_procurementMethodType)
    config.scan("openprocurement.tender.core.views")
    config.scan("openprocurement.tender.core.procedure.views")
    config.scan("openprocurement.tender.core.subscribers")
    config.registry.registerAdapter(TenderConfigurator, (ITender, IRequest), IContentConfigurator)

    # search for plugins
    settings = config.get_settings()
    plugins = settings.get("plugins") and [plugin.strip() for plugin in settings["plugins"].split(",")]
    for entry_point in iter_entry_points("openprocurement.tender.core.plugins"):
        if not plugins or entry_point.name in plugins:
            plugin = entry_point.load()
            plugin(config)
