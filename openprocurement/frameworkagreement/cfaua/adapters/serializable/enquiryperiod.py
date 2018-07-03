# /home/andriis/ramki/openprocurement.buildout/src/openprocurement.tender.openeu/openprocurement/tender/openeu/models.py:610
from openprocurement.tender.core.utils import calculate_business_date
from openprocurement.tender.openeu.constants import QUESTIONS_STAND_STILL
from openprocurement.tender.openua.constants import ENQUIRY_STAND_STILL_TIME


class TenderEnquiryPeriod(object):
    def __init__(self, tender):
        self.context = tender

    def __call__(self, *args, **kwargs):
        enquiryPeriod_class = self.context._fields['enquiryPeriod']
        endDate = calculate_business_date(self.context.tenderPeriod.endDate, -QUESTIONS_STAND_STILL, self.context)
        return enquiryPeriod_class(dict(
            startDate=self.context.tenderPeriod.startDate,
            endDate=endDate,
            invalidationDate=self.context.enquiryPeriod and self.context.enquiryPeriod.invalidationDate,
            clarificationsUntil=calculate_business_date(endDate, ENQUIRY_STAND_STILL_TIME, self.context, True)))
