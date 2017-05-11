# -*- coding: utf-8 -*-
from openprocurement.tender.esco.models import TenderESCOEU


def includeEU(config):
    config.add_tender_procurementMethodType(TenderESCOEU)
    config.scan("openprocurement.tender.esco.views")
