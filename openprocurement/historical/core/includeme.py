# -*- coding: utf-8 -*-
from logging import getLogger
from pkg_resources import get_distribution
from openprocurement.historical.core.utils import (
    extract_doc,
    HasRequestMethod,
)
from openprocurement.historical.core.constants import PREDICATE_NAME


PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def includeme(config):
    LOGGER.info('Init historical.core plugin')
    config.add_request_method(extract_doc, 'extract_doc_versioned')
    config.add_route_predicate(PREDICATE_NAME, HasRequestMethod)
