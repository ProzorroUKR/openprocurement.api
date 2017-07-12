from cornice.errors import Errors
from pyramid.events import subscriber
from pyramid.request import Request
from pyramid.registry import Registry
from openprocurement.api.utils import error_handler
from openprocurement.tender.core.events import TenderInitializeEvent
from openprocurement.tender.core.utils import get_now, calculate_business_date
from openprocurement.tender.core.models import EnquiryPeriod
from openprocurement.tender.openua.constants import ENQUIRY_STAND_STILL_TIME
from openprocurement.tender.openeu.constants import QUESTIONS_STAND_STILL
from openprocurement.tender.esco.models import Tender

@subscriber(TenderInitializeEvent, procurementMethodType="esco.EU")
def tender_init_handler(event):
    """ initialization handler for esco eu tenders """
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

    check_submission_method_details(tender)


# TODO: temporary decision, while esco auction is not ready. Remove after adding auction. Remove field 'submissionMethodDetails' in openprocurement.tender.esco.models.Tender
def check_submission_method_details(tender):
    errors = Errors()
    errors.request = Request({})
    errors.request.registry = Registry()
    if tender.submissionMethodDetails is not None and tender.submissionMethodDetails != Tender.submissionMethodDetails.default:
        errors.add(
            'data',
            'submissionMethodDetails',
            'Invalid field value \'{0}\'. Only \'{1}\' is allowed while auction for this type of procedure is not ready.'.
                format(tender.submissionMethodDetails, Tender.submissionMethodDetails.default))
        errors.status = 403
        raise error_handler(errors, request_params=False)
