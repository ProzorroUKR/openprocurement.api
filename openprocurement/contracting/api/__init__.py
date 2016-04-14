# -*- coding: utf-8 -*-
from pyramid.events import ContextFound
from logging import getLogger
from pkg_resources import get_distribution
from openprocurement.contracting.api.design import add_design
from openprocurement.contracting.api.utils import contract_from_data

PKG = get_distribution(__package__)

LOGGER = getLogger(PKG.project_name)


def includeme(config):
    LOGGER.info('Init contracting plugin.')
    add_design()
    config.add_request_method(contract_from_data)
    config.scan("openprocurement.contracting.api.views")
