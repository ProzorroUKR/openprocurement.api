from logging import getLogger

from openprocurement.tender.core.utils import register_route_prefix
from openprocurement.tender.open.constants import (
    OPEN_ROUTE_PREFIX,
    OpenProcurementMethodType,
)

LOGGER = getLogger("openprocurement.tender.open")


def includeme(config):
    LOGGER.info("Init tender.open plugin.")
    register_route_prefix(OPEN_ROUTE_PREFIX, OpenProcurementMethodType)
    config.scan("openprocurement.tender.open.procedure.views")
