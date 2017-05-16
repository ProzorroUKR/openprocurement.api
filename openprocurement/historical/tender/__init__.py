# -*- coding: utf-8 -*-
from logging import getLogger
from pkg_resources import get_distribution
from openprocurement.historical.core.utils import (
    HasRequestMethod,
)
from openprocurement.historical.core.constants import (
    PREDICATE_NAME
)

PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def includeme(config):
    LOGGER.info('Init historical.tender plugin.')
    pred_list = config.get_predlist('route')
    if PREDICATE_NAME not in pred_list.sorter.names:
        LOGGER.warn('historical.core package not plugged')
        config.add_route_predicate(PREDICATE_NAME, HasRequestMethod)
    config.scan('openprocurement.historical.tender.views')
