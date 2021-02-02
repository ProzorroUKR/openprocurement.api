from pyramid.events import subscriber

from openprocurement.tender.core.events import TenderInitializeEvent
from openprocurement.tender.core.utils import (
    get_now,
    calculate_tender_business_date,
    calculate_clarif_business_date,
)
from openprocurement.tender.core.models import EnquiryPeriod
from openprocurement.tender.cfaua.constants import QUESTIONS_STAND_STILL


@subscriber(TenderInitializeEvent, procurementMethodType="closeFrameworkAgreementUA")
def tender_init_handler(event):
    """ initialization handler for closeFrameworkAgreementUA tenders """
    tender = event.tender
    end_date = calculate_tender_business_date(tender.tenderPeriod.endDate, -QUESTIONS_STAND_STILL, tender)
    clarifications_until = calculate_clarif_business_date(end_date, QUESTIONS_STAND_STILL, tender, True)
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
