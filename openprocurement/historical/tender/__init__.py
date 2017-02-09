# -*- coding: utf-8 -*-
from logging import getLogger
from pkg_resources import get_distribution
from openprocurement.historical.core.utils import (
    HasRequestMethod,
    route_predicate_name
)

PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def includeme(config):
    LOGGER.info('Init historical.tender plugin.')
    pred_list = config.get_predlist('route')
    if route_predicate_name not in pred_list.sorter.names:
        LOGGER.warn('historical.core package not plugged')
        config.add_route_predicate(route_predicate_name, HasRequestMethod)
    config.scan('openprocurement.historical.tender.views')
