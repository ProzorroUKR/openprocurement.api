# -*- coding: utf-8 -*-
from logging import getLogger

LOGGER = getLogger("openprocurement.framework.dps")


def includeme(config):
    LOGGER.info("Init framework.dps plugin.")
    config.scan("openprocurement.framework.dps.procedure.views")
