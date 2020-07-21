# -*- coding: utf-8 -*-
from pyramid.events import subscriber
from openprocurement.tender.core.events import TenderInitializeEvent
from openprocurement.api.utils import get_now
from openprocurement.tender.pricequotation.constants import\
    PMT


@subscriber(TenderInitializeEvent, procurementMethodType=PMT)
def tender_init_handler(event):
    """ Initialization handler for Price Quotation tenders """
    tender = event.tender
    now = get_now()

    if not tender.tenderPeriod.startDate:
        tender.tenderPeriod.startDate = now
    tender.date = now
