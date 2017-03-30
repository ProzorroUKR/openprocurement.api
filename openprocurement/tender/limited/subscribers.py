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
def tender_init_handler_reporting(event):
    """ initialization handler for tenders 'reporting'"""
    event.tender.date = get_now()

# initialization handler for tenders 'negotiation'
tender_init_handler_negotiation = subscriber(TenderInitializeEvent, procurementMethodType="negotiation")(tender_init_handler_base)

# initialization handler for tenders 'negotiation.quick'
tender_init_handler_negotiation_quick = subscriber(TenderInitializeEvent, procurementMethodType="negotiation.quick")(tender_init_handler_base)
