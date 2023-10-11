# -*- coding: utf-8 -*-
from logging import getLogger

LOGGER = getLogger("openprocurement.tender.esco")


def includeme(config):
    LOGGER.info("Init tender.esco plugin.")
    config.scan("openprocurement.tender.esco.procedure.views")
