# -*- coding: utf-8 -*-
from openprocurement.tender.belowthreshold.models import Tender
from openprocurement.tender.core import includeme as includeme_core

def includeme(config):
    if not hasattr(config, 'add_tender_procurementMethodType'):
        includeme_core(config)
    print "Init below"
    config.add_tender_procurementMethodType(Tender)
    config.scan("openprocurement.tender.belowthreshold.views")
