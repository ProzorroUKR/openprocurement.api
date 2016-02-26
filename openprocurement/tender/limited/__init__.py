from openprocurement.tender.limited.models import ReportingTender, NegotiationTender


def includeme(config):
    config.add_tender_procurementMethodType(ReportingTender)
    config.scan("openprocurement.tender.limited.views")


def includeme_negotiation(config):
    config.add_tender_procurementMethodType(NegotiationTender)
    config.scan("openprocurement.tender.limited.views")
