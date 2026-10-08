from logging import getLogger

from openprocurement.tender.core.utils import register_route_prefix
from openprocurement.tender.open.constants import (
    OPEN_PROCUREMENT_METHOD_TYPES,
    OPEN_ROUTE_PREFIX,
)

LOGGER = getLogger("openprocurement.tender.open")


def includeme(config):
    LOGGER.info("Init tender.open plugin.")
    register_route_prefix(OPEN_ROUTE_PREFIX, OPEN_PROCUREMENT_METHOD_TYPES)
    config.scan("openprocurement.tender.open.procedure.views")
