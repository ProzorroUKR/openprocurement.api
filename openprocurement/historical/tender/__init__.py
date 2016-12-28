# -*- coding: utf-8 -*-
from logging import getLogger
from pkg_resources import get_distribution
from openprocurement.historical.tender.utils import extract_tender_version

PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def includeme(config):
    LOGGER.info('Init historical.tender plugin.')
    config.add_request_method(extract_tender_version, 'historical_tender', reify=True)
    config.scan('openprocurement.historical.tender.views')
