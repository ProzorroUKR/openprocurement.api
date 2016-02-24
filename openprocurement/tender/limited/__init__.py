from openprocurement.tender.limited.models import Tender
from openprocurement.tender.limited.models_negotiation import Tender as NegotiationTender


def includeme(config):
    config.add_tender_procurementMethodType(Tender)
    config.scan("openprocurement.tender.limited.views")


def includeme_negotiation(config):
    config.add_tender_procurementMethodType(NegotiationTender)
    config.scan("openprocurement.tender.limited.views")
