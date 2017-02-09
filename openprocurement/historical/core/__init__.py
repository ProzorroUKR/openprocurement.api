# -*- coding: utf-8 -*-
from logging import getLogger
from pkg_resources import get_distribution
from openprocurement.historical.core.utils import (
    extract_doc,
    HasRequestMethod,
    route_predicate_name
)


PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def includeme(config):
    LOGGER.info('Init historical.core plugin')
    config.add_request_method(extract_doc, 'extract_doc_versioned')
    config.add_route_predicate(route_predicate_name,
                               HasRequestMethod)
