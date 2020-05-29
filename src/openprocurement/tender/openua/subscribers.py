from pyramid.events import subscriber
from openprocurement.tender.core.events import TenderInitializeEvent
from openprocurement.tender.core.utils import (
    get_now,
    calculate_tender_business_date,
    calculate_clarif_business_date,
)

from openprocurement.tender.core.models import EnquiryPeriod
from openprocurement.tender.openua.constants import ENQUIRY_PERIOD_TIME, ENQUIRY_STAND_STILL_TIME


@subscriber(TenderInitializeEvent, procurementMethodType="aboveThresholdUA")
def tender_init_handler(event):
    """ initialization handler for openua tenders """
    tender = event.tender
    end_date = calculate_tender_business_date(tender.tenderPeriod.endDate, -ENQUIRY_PERIOD_TIME, tender)
    clarifications_until = calculate_clarif_business_date(end_date, ENQUIRY_STAND_STILL_TIME, tender, True)
    tender.enquiryPeriod = EnquiryPeriod(
        dict(
            startDate=tender.tenderPeriod.startDate,
            endDate=end_date,
            invalidationDate=tender.enquiryPeriod and tender.enquiryPeriod.invalidationDate,
            clarificationsUntil=clarifications_until,
        )
    )
    now = get_now()
    tender.date = now
    if tender.lots:
        for lot in tender.lots:
            lot.date = now
