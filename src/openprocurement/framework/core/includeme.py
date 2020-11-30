# -*- coding: utf-8 -*-
from logging import getLogger

from pkg_resources import iter_entry_points

from openprocurement.framework.core.utils import (
    extract_doc,
    register_framework_frameworkType,
    isFramework,
    framework_from_data,
)

LOGGER = getLogger("openprocurement.historical.core")


def includeme(config):
    from openprocurement.framework.core.design import add_design
    LOGGER.info("Init framework.core plugin")

    add_design()
    config.add_request_method(extract_doc, "framework", reify=True)

    # tender procurementMethodType plugins support
    config.registry.framework_frameworkTypes = {}
    config.add_route_predicate("frameworkType", isFramework)
    config.add_request_method(framework_from_data)
    config.add_directive("add_framework_frameworkTypes", register_framework_frameworkType)
    config.scan("openprocurement.framework.core.views")

    # search for plugins
    settings = config.get_settings()
    plugins = settings.get("plugins") and [plugin.strip() for plugin in settings["plugins"].split(",")]
    for entry_point in iter_entry_points("openprocurement.framework.core.plugins"):
        if not plugins or entry_point.name in plugins:
            plugin = entry_point.load()
            plugin(config)
