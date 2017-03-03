# -*- coding: utf-8 -*-
from openprocurement.tender.belowthreshold.models import Tender

def includeme(config):
    config.add_tender_procurementMethodType(Tender)
    print "Init below"
    config.scan("openprocurement.tender.belowthreshold.views")
