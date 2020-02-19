# -*- coding: utf-8 -*-
import os
from logging import getLogger
from pkg_resources import iter_entry_points
from zope.configuration.xmlconfig import file as ZcmlFile
from pyramid.interfaces import IRequest

import openprocurement.agreement.core
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.agreement.core.interfaces import IAgreement
from openprocurement.agreement.core.adapters.configurator import BaseAgreementConfigurator
from openprocurement.agreement.core.design import add_design
from openprocurement.agreement.core.resource import IsAgreement
from openprocurement.agreement.core.utils import register_agreement_type, agreement_from_data, extract_agreement


LOGGER = getLogger("openprocurement.agreement.core")


def includeme(config):  # pragma: no cover
    LOGGER.info("Init agreement.core plugin.")

    add_design()
    config.registry.agreements_types = {}
    config.add_route_predicate("agreementType", IsAgreement)
    config.add_directive("add_agreement_type", register_agreement_type)
    config.add_request_method(extract_agreement, "agreement", reify=True)
    config.add_request_method(agreement_from_data)
    config.registry.registerAdapter(BaseAgreementConfigurator, (IAgreement, IRequest), IContentConfigurator)

    config.scan("openprocurement.agreement.core.views")
    ZcmlFile(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "configure.zcml"),
        package=openprocurement.agreement.core,
    )
    # search for plugins
    settings = config.get_settings()
    plugins = settings.get("plugins") and [plugin.strip() for plugin in settings["plugins"].split(",")]
    for entry_point in iter_entry_points("openprocurement.agreements.core.plugins"):
        if not plugins or entry_point.name in plugins:
            plugin = entry_point.load()
            plugin(config)
