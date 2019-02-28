from zope.component import getAdapter
from pyramid.events import subscriber

from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.tender.core.events import TenderInitializeEvent
from openprocurement.tender.core.utils import get_now, calculate_business_date
from openprocurement.tender.core.models import EnquiryPeriod


@subscriber(TenderInitializeEvent, procurementMethodType="closeFrameworkAgreementUA")
def tender_init_handler(event):
    """ initialization handler for closeFrameworkAgreementUA tenders """
    tender = event.tender
    config = getAdapter(tender, IContentConfigurator)
    endDate = calculate_business_date(tender.tenderPeriod.endDate,
                                      -config.questions_stand_still, tender)
    tender.enquiryPeriod = EnquiryPeriod(dict(startDate=tender.tenderPeriod.startDate,
                                         endDate=endDate,
                                         invalidationDate=tender.enquiryPeriod and tender.enquiryPeriod.invalidationDate,
                                         clarificationsUntil=calculate_business_date(endDate, config.enquiry_stand_still, tender, True)))
    now = get_now()
    tender.date = now
    if tender.lots:
        for lot in tender.lots:
            lot.date = now
