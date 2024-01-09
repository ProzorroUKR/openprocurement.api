from openprocurement.api.database import COLLECTION_CLASSES
from openprocurement.planning.api.database import PlanCollection
from openprocurement.planning.api.utils import extract_plan_doc
from logging import getLogger

LOGGER = getLogger("openprocurement.planning.api")


def includeme(config):
    LOGGER.info("Init planning.api plugin")

    COLLECTION_CLASSES["plans"] = PlanCollection

    config.add_request_method(extract_plan_doc, "plan_doc", reify=True)
    config.scan("openprocurement.planning.api.procedure.views")
