# -*- coding: utf-8 -*-
from logging import getLogger


LOGGER = getLogger("openprocurement.tender.pricequotation")


def includeme(config):
    LOGGER.info("Init tender.pricequotation plugin.")
    config.scan("openprocurement.tender.pricequotation.procedure.views")
