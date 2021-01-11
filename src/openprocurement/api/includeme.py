# -*- coding: utf-8 -*-
from logging import getLogger
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator, IOPContent
from openprocurement.api.adapters import ContentConfigurator
from openprocurement.api.utils import get_content_configurator, request_get_now, json_body

LOGGER = getLogger("openprocurement.api")


def includeme(config):
    LOGGER.info("Init api plugin.")

    config.scan("openprocurement.api.views")
    config.scan("openprocurement.api.subscribers")
    config.registry.registerAdapter(ContentConfigurator, (IOPContent, IRequest), IContentConfigurator)
    config.add_request_method(get_content_configurator, "content_configurator", reify=True)
    config.add_request_method(request_get_now, "now", reify=True)
    config.add_request_method(json_body, "json", reify=True)
