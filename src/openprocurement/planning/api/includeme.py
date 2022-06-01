from pyramid.events import ContextFound
from openprocurement.api.database import COLLECTION_CLASSES
from openprocurement.planning.api.database import PlanCollection
from openprocurement.planning.api.utils import plan_from_data, extract_plan_doc, extract_plan, set_logging_context
from logging import getLogger

LOGGER = getLogger("openprocurement.planning.api")


def includeme(config):
    LOGGER.info("Init planning.api plugin")

    COLLECTION_CLASSES["plans"] = PlanCollection

    config.add_subscriber(set_logging_context, ContextFound)
    config.add_request_method(extract_plan_doc, "plan_doc", reify=True)
    config.add_request_method(extract_plan, "plan", reify=True)
    config.add_request_method(extract_plan)
    config.add_request_method(plan_from_data)
    config.scan("openprocurement.planning.api.views")
