from openprocurement.tender.openeu.models import Tender


def includeme(config):
    config.add_tender_procurementMethodType(Tender)
    config.scan("openprocurement.tender.openeu.views")
