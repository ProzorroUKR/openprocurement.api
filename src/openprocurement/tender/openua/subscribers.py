from pyramid.events import subscriber
from openprocurement.tender.core.events import TenderInitializeEvent
from openprocurement.tender.core.utils import (
    get_now,
    calculate_tender_business_date,
    calculate_clarifications_business_date,
)

from openprocurement.tender.core.models import EnquiryPeriod
from openprocurement.tender.openua.constants import ENQUIRY_PERIOD_TIME, ENQUIRY_STAND_STILL_TIME


@subscriber(TenderInitializeEvent, procurementMethodType="aboveThresholdUA")
def tender_init_handler(event):
    """ initialization handler for openua tenders """
    tender = event.tender
    endDate = calculate_tender_business_date(tender.tenderPeriod.endDate, -ENQUIRY_PERIOD_TIME, tender)
    clarificationsUntil = calculate_clarifications_business_date(endDate, ENQUIRY_STAND_STILL_TIME, tender, True)
    tender.enquiryPeriod = EnquiryPeriod(
        dict(
            startDate=tender.tenderPeriod.startDate,
            endDate=endDate,
            invalidationDate=tender.enquiryPeriod and tender.enquiryPeriod.invalidationDate,
            clarificationsUntil=clarificationsUntil,
        )
    )
    now = get_now()
    tender.date = now
    if tender.lots:
        for lot in tender.lots:
            lot.date = now
