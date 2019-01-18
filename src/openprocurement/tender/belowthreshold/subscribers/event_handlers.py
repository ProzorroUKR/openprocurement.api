# -*- coding: utf-8 -*-
from pyramid.events import subscriber
from openprocurement.tender.core.events import TenderInitializeEvent
from openprocurement.api.utils import get_now


@subscriber(TenderInitializeEvent, procurementMethodType="belowThreshold")
def tender_init_handler(event):
    """ initialization handler for belowThreshold tenders """
    tender = event.tender
    if not tender.enquiryPeriod.startDate:
        tender.enquiryPeriod.startDate = get_now()
    if not tender.tenderPeriod.startDate:
        tender.tenderPeriod.startDate = tender.enquiryPeriod.endDate
    now = get_now()
    tender.date = now
    if tender.lots:
        for lot in tender.lots:
            lot.date = now
