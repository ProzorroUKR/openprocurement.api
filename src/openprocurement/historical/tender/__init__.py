# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.historical.core.utils import HasRequestMethod
from openprocurement.historical.core.constants import PREDICATE_NAME

LOGGER = getLogger("openprocurement.historical.tender")


def includeme(config):
    LOGGER.info("Init historical.tender plugin.")
    pred_list = config.get_predlist("route")
    if PREDICATE_NAME not in pred_list.sorter.names:
        LOGGER.warn("historical.core package not plugged")
        config.add_route_predicate(PREDICATE_NAME, HasRequestMethod)
    config.scan("openprocurement.historical.tender.views")
