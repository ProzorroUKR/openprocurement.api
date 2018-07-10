# openprocurement.tender.openeu.models.Tender#validate_tenderPeriod
from openprocurement.tender.core.utils import calculate_business_date
from datetime import timedelta
from openprocurement.api.utils import get_now
from schematics.exceptions import ValidationError
from openprocurement.frameworkagreement.cfaua.constants import (
    TENDERING_DURATION,
    TENDERING_DAYS
)

class TenderPeriodValidate(object):
    def __init__(self, tender):
        self.context = tender

    def __call__(self, cls, data, period):
        if not data['_rev'] and calculate_business_date(get_now(), -timedelta(minutes=10)) >= period.startDate:
            raise ValidationError(u"tenderPeriod.startDate should be in greater than current date")
        if period and calculate_business_date(period.startDate, TENDERING_DURATION, data) > period.endDate:
            raise ValidationError(u"tenderPeriod should be greater than {} days".format(TENDERING_DAYS))