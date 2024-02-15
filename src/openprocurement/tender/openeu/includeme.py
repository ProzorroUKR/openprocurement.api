# -*- coding: utf-8 -*-
from logging import getLogger

LOGGER = getLogger("openprocurement.tender.openeu")


def includeme(config):
    LOGGER.info("Init tender.openeu plugin.")
    config.scan("openprocurement.tender.openeu.procedure.views")
