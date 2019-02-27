from pyramid.events import subscriber
from openprocurement.tender.core.events import TenderInitializeEvent
from openprocurement.tender.core.utils import get_now, calculate_business_date
from openprocurement.tender.core.models import EnquiryPeriod
from openprocurement.tender.openua.constants import ENQUIRY_STAND_STILL_TIME
from openprocurement.tender.openeu.constants import QUESTIONS_STAND_STILL


@subscriber(TenderInitializeEvent, procurementMethodType="aboveThresholdEU")
def tender_init_handler(event):
    """ initialization handler for openeu tenders """
    tender = event.tender
    endDate = calculate_business_date(tender.tenderPeriod.endDate,
                                      -QUESTIONS_STAND_STILL, tender)
    tender.enquiryPeriod = EnquiryPeriod(dict(startDate=tender.tenderPeriod.startDate,
                                         endDate=endDate,
                                         invalidationDate=tender.enquiryPeriod and tender.enquiryPeriod.invalidationDate,
                                         clarificationsUntil=calculate_business_date(endDate, ENQUIRY_STAND_STILL_TIME, tender, True)))
    now = get_now()
    tender.date = now
    if tender.lots:
        for lot in tender.lots:
            lot.date = now
