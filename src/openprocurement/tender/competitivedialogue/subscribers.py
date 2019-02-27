from pyramid.events import subscriber
from openprocurement.tender.core.events import TenderInitializeEvent
from openprocurement.tender.core.utils import get_now, calculate_business_date
from openprocurement.tender.openeu.constants import (
    TENDERING_DURATION as TENDERING_DURATION_EU,
)
from openprocurement.tender.openua.constants import (
    TENDER_PERIOD as TENDERING_DURATION_UA,
)
from openprocurement.tender.openua.subscribers import tender_init_handler as tender_init_handler_ua
from openprocurement.tender.openeu.subscribers import tender_init_handler as tender_init_handler_eu


@subscriber(TenderInitializeEvent, procurementMethodType="competitiveDialogueEU.stage2")
def tender_init_handler_1(event):
    """ initialization handler for tenders """
  #  import pdb; pdb.set_trace()
    tender = event.tender
    tender.tenderPeriod.endDate = calculate_business_date(tender.tenderPeriod.startDate, TENDERING_DURATION_EU, tender)
    tender_init_handler_eu(event)


@subscriber(TenderInitializeEvent, procurementMethodType="competitiveDialogueUA.stage2")
def tender_init_handler_2(event):
    """ initialization handler for tenders """
 #   import pdb; pdb.set_trace()
    tender = event.tender
    tender.tenderPeriod.endDate = calculate_business_date(tender.tenderPeriod.startDate, TENDERING_DURATION_UA, tender)
    tender_init_handler_ua(event)


@subscriber(TenderInitializeEvent, procurementMethodType="competitiveDialogueEU")
def tender_init_handler_3(event):
    """ initialization handler for tenders """
   # tender = event.tender
   # tender.tenderPeriod.endDate = calculate_business_date(tender.tenderPeriod.startDate, TENDERING_DURATION_EU, tender)
    tender_init_handler_eu(event)
    # import pdb; pdb.set_trace()


@subscriber(TenderInitializeEvent, procurementMethodType="competitiveDialogueUA")
def tender_init_handler_4(event):
    """ initialization handler for tenders """
    #tender = event.tender
    #tender.tenderPeriod.endDate = calculate_business_date(tender.tenderPeriod.startDate, TENDERING_DURATION_UA, tender)
    tender_init_handler_ua(event)
    # import pdb; pdb.set_trace()
