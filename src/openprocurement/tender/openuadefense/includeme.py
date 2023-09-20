# -*- coding: utf-8 -*-
from logging import getLogger

LOGGER = getLogger("openprocurement.tender.openuadefense")


def includeme(config):
    LOGGER.info("Init tender.openuadefense plugin.")
    config.scan("openprocurement.tender.openuadefense.procedure.views")
