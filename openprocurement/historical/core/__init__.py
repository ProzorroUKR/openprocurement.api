# -*- coding: utf-8 -*-
from logging import getLogger
from pkg_resources import get_distribution
from openprocurement.historical.core.utils import (
    extract_header,
    add_header
)


PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def includeme(config):
    LOGGER.info('Loading historical.core plugin')
    config.add_request_method(extract_header)
    config.add_request_method(add_header)
