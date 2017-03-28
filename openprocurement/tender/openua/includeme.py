from openprocurement.tender.openua.models import Tender

def includeme(config):
    config.add_tender_procurementMethodType(Tender)
    print "init openua"
    config.scan("openprocurement.tender.openua.views")
    config.scan("openprocurement.tender.openua.subscribers")
