from openprocurement.tender.openua.models import Tender
from openprocurement.tender.core import includeme as includeme_core

def includeme(config):
    if not hasattr(config, 'add_tender_procurementMethodType'):
        includeme_core(config)
        config.add_tender_procurementMethodType(Tender)
    else:
        config.add_tender_procurementMethodType(Tender)
    print "init openua"
    config.scan("openprocurement.tender.openua.views")
