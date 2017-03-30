from pyramid.events import subscriber
from openprocurement.tender.core.events import TenderInitializeEvent
from openprocurement.tender.core.utils import get_now, calculate_business_date


@subscriber(TenderInitializeEvent, procurementMethodType="reporting")
def tender_init_handler(event):
    """ initialization handler for tenders """
    event.tender.date = get_now()


@subscriber(TenderInitializeEvent, procurementMethodType="negotiation")
def tender_init_handler(event):
    """ initialization handler for tenders """
    event.tender.date = get_now()


@subscriber(TenderInitializeEvent, procurementMethodType="negotiation.quick")
def tender_init_handler(event):
    """ initialization handler for tenders """
    event.tender.date = get_now()
