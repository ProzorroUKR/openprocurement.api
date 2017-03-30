from pyramid.events import subscriber
from openprocurement.tender.core.events import TenderInitializeEvent
from openprocurement.tender.core.utils import get_now, calculate_business_date


def tender_init_handler_base(event):
    tender = event.tender
    tender.date = get_now()
    if tender.lots:
        for lot in tender.lots:
            lot.date = get_now()


@subscriber(TenderInitializeEvent, procurementMethodType="reporting")
def tender_init_handler_1(event):
    """ initialization handler for tenders """
    event.tender.date = get_now()


@subscriber(TenderInitializeEvent, procurementMethodType="negotiation")
def tender_init_handler_2(event):
    """ initialization handler for tenders """
    tender_init_handler_base(event)


@subscriber(TenderInitializeEvent, procurementMethodType="negotiation.quick")
def tender_init_handler_3(event):
    """ initialization handler for tenders """
    tender_init_handler_base(event)
