# -*- coding: utf-8 -*-
import os
from logging import getLogger
from pkg_resources import get_distribution, iter_entry_points
from zope.configuration.xmlconfig import file as ZcmlFile
from pyramid.interfaces import IRequest

import openprocurement.agreement.core
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.agreement.core.interfaces import IAgreement
from openprocurement.agreement.core.adapters.configurator import BaseAgreementConfigurator
from openprocurement.agreement.core.design import add_design
from openprocurement.agreement.core.resource import (
    extract_agreement,
    IsAgreenent
    )

PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def includeme(config):
    LOGGER.info("Load agreement.core plugin")
    add_design()
    config.add_route_predicate(
        'agreementType',
        IsAgreenent
    )
    config.registry.registerAdapter(
        BaseAgreementConfigurator,
        (IAgreement, IRequest),
        IContentConfigurator
        )

    config.scan("openprocurement.agreement.core.views")
    ZcmlFile(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configure.zcml'),
        package=openprocurement.agreement.core
    )
