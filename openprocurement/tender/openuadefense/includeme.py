from openprocurement.tender.openuadefense.models import Tender


def includeme(config):
    config.add_tender_procurementMethodType(Tender)
    config.scan("openprocurement.tender.openuadefense.views")
    config.scan("openprocurement.tender.openuadefense.subscribers")
