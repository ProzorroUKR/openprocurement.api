# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import json_body

LOGGER = getLogger("openprocurement.api")


def includeme(config):
    LOGGER.info("Init api plugin.")

    config.scan("openprocurement.api.views")
    config.scan("openprocurement.api.subscribers")
    config.add_request_method(json_body, "json", reify=True)
