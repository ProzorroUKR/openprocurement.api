from pyramid.events import subscriber
from openprocurement.tender.core.events import TenderInitializeEvent
from openprocurement.tender.core.utils import get_now, calculate_business_date
from openprocurement.tender.core.models import EnquiryPeriod
from openprocurement.tender.openuadefense.constants import (
    ENQUIRY_STAND_STILL_TIME,
    ENQUIRY_PERIOD_TIME
)


@subscriber(TenderInitializeEvent, procurementMethodType="aboveThresholdUA.defense")
def tender_init_handler(event):
    """ initialization handler for openuadefence tenders """
    tender = event.tender
    endDate = calculate_business_date(tender.tenderPeriod.endDate,
                                      -ENQUIRY_PERIOD_TIME, tender, True)
    tender.enquiryPeriod = EnquiryPeriod(dict(startDate=tender.tenderPeriod.startDate,
                                         endDate=endDate,
                                         invalidationDate=tender.enquiryPeriod and tender.enquiryPeriod.invalidationDate,
                                         clarificationsUntil=calculate_business_date(endDate, ENQUIRY_STAND_STILL_TIME, tender, True)))
    now = get_now()
    tender.date = now
    if tender.lots:
        for lot in tender.lots:
            lot.date = now
