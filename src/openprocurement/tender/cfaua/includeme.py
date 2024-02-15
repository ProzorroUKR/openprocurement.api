# -*- coding: utf-8 -*-
from logging import getLogger

LOGGER = getLogger("openprocurement.tender.cfaua")


def includeme(config):
    LOGGER.info("Init tender.cfaua plugin.")
    config.scan("openprocurement.tender.cfaua.procedure.views")
