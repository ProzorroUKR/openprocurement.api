from openprocurement.tender.limited.models import (ReportingTender,
                                                   NegotiationTender,
                                                   NegotiationQuickTender)


def includeme(config):
    config.add_tender_procurementMethodType(ReportingTender)
    config.scan("openprocurement.tender.limited.views")


def includeme_negotiation(config):
    config.add_tender_procurementMethodType(NegotiationTender)
    config.scan("openprocurement.tender.limited.views")


def includeme_negotiation_quick(config):
    config.add_tender_procurementMethodType(NegotiationQuickTender)
    config.scan("openprocurement.tender.limited.views")
