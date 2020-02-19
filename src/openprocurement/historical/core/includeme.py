# -*- coding: utf-8 -*-
from logging import getLogger
from pkg_resources import iter_entry_points
from openprocurement.historical.core.utils import extract_doc, HasRequestMethod
from openprocurement.historical.core.constants import PREDICATE_NAME


LOGGER = getLogger("openprocurement.historical.core")


def includeme(config):
    LOGGER.info("Init historical.core plugin")
    config.add_request_method(extract_doc, "extract_doc_versioned")
    config.add_route_predicate(PREDICATE_NAME, HasRequestMethod)

    # search for plugins
    settings = config.get_settings()
    plugins = settings.get("plugins") and [plugin.strip() for plugin in settings["plugins"].split(",")]
    for entry_point in iter_entry_points("openprocurement.historical.core.plugins"):
        if not plugins or entry_point.name in plugins:
            plugin = entry_point.load()
            plugin(config)
