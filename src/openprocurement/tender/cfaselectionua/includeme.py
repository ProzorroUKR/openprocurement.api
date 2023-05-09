# -*- coding: utf-8 -*-
from logging import getLogger

LOGGER = getLogger("openprocurement.tender.cfaselectionua")


def includeme(config):
    LOGGER.info("Init tender.cfaselectionua plugin.")
    config.scan("openprocurement.tender.cfaselectionua.procedure.views")
