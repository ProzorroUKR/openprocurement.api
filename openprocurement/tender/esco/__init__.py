# -*- coding: utf-8 -*-
from openprocurement.tender.esco.models import TenderESCOUA, TenderESCOEU

def includeme(config):
    config.add_tender_procurementMethodType(TenderESCOUA)
    config.add_tender_procurementMethodType(TenderESCOEU)
    config.scan("openprocurement.tender.esco.views")
