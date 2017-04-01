# -*- coding: utf-8 -*-
from openprocurement.tender.core.adapters import TenderConfigurator
from openprocurement.tender.limited.models import (
    ReportingTender, NegotiationTender, NegotiationQuickTender
)


class TenderReportingConfigurator(TenderConfigurator):
    """ Reporting Tender configuration adapter """

    name = "Reporting Tender configurator"
    model = ReportingTender

    @property
    def edit_accreditation(self):
        raise NotImplemented


class TenderNegotiationConfigurator(TenderConfigurator):
    """ Negotiation Tender configuration adapter """

    name = "Negotiation Tender configurator"
    model = NegotiationTender

    @property
    def edit_accreditation(self):
        raise NotImplemented


class TenderNegotiationQuickConfigurator(TenderNegotiationConfigurator):
    """ Negotiation Quick Tender configuration adapter """

    name = "Negotiation Quick Tender configurator"
    model = NegotiationQuickTender
