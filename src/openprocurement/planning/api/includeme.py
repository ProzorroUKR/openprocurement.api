from logging import getLogger

from openprocurement.planning.api.database import PlanCollection
from openprocurement.planning.api.utils import extract_plan_doc

LOGGER = getLogger("openprocurement.planning.api")


def includeme(config):
    LOGGER.info("Init planning.api plugin")

    config.registry.mongodb.add_collection("plans", PlanCollection)

    config.add_request_method(extract_plan_doc, "plan_doc", reify=True)
    config.scan("openprocurement.planning.api.procedure.views")
