from schematics.exceptions import ValidationError

from openprocurement.tender.cfaselectionua.constants import TENDERING_DURATION
from openprocurement.tender.openua.validation import validate_tender_period_duration


class TenderPeriodValidate(object):
    def __init__(self, tender):
        self.context = tender

    def __call__(self, cls, data, period):
        if (
            period
            and period.startDate
            and data.get("enquiryPeriod")
            and data.get("enquiryPeriod").endDate
            and period.startDate < data.get("enquiryPeriod").endDate
        ):
            raise ValidationError(u"period should begin after enquiryPeriod")
        if (
            period
            and period.startDate
            and period.endDate
        ):
            validate_tender_period_duration(data, period, TENDERING_DURATION)
