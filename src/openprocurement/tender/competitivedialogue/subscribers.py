from pyramid.events import subscriber
from openprocurement.tender.core.events import TenderInitializeEvent
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.openeu.constants import TENDERING_DURATION as TENDERING_DURATION_EU
from openprocurement.tender.openua.constants import TENDERING_DURATION as TENDERING_DURATION_UA
from openprocurement.tender.openua.subscribers import tender_init_handler as tender_init_handler_ua
from openprocurement.tender.openeu.subscribers import tender_init_handler as tender_init_handler_eu


@subscriber(TenderInitializeEvent, procurementMethodType="competitiveDialogueEU.stage2")
def tender_init_handler_eu_stage2(event):
    """ initialization handler for tenders """
    tender = event.tender
    tender.tenderPeriod.endDate = calculate_tender_business_date(
        tender.tenderPeriod.startDate, TENDERING_DURATION_EU, tender
    )
    tender_init_handler_eu(event)


@subscriber(TenderInitializeEvent, procurementMethodType="competitiveDialogueUA.stage2")
def tender_init_handler_ua_stage2(event):
    """ initialization handler for tenders """
    tender = event.tender
    tender.tenderPeriod.endDate = calculate_tender_business_date(
        tender.tenderPeriod.startDate, TENDERING_DURATION_UA, tender
    )
    tender_init_handler_ua(event)


@subscriber(TenderInitializeEvent, procurementMethodType="competitiveDialogueEU")
def tender_init_handler_eu_stage1(event):
    """ initialization handler for tenders """
    tender_init_handler_eu(event)


@subscriber(TenderInitializeEvent, procurementMethodType="competitiveDialogueUA")
def tender_init_handler_ua_stage1(event):
    """ initialization handler for tenders """
    tender_init_handler_ua(event)
