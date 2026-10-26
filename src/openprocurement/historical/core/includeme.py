from logging import getLogger

from openprocurement.historical.core.constants import PREDICATE_NAME
from openprocurement.historical.core.utils import HasRequestMethod, extract_doc

LOGGER = getLogger("openprocurement.historical.core")


def includeme(config):
    LOGGER.info("Init historical.core plugin")
    config.add_request_method(extract_doc, "extract_doc_versioned")
    config.add_route_predicate(PREDICATE_NAME, HasRequestMethod)
