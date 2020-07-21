# -*- coding: utf-8 -*-
from openprocurement.tender.core.adapters import TenderConfigurator
from openprocurement.tender.pricequotation.models import PriceQuotationTender


class PQTenderConfigurator(TenderConfigurator):
    """ Price Quotation Tender configuration adapter """

    name = "Price Quotation Tender configurator"
    model = PriceQuotationTender
