# openprocurement.tender.openeu.models.Tender#validate_tenderPeriod
from openprocurement.api.utils import is_new_created
from openprocurement.tender.cfaua.constants import TENDERING_DURATION
from openprocurement.tender.openua.validation import (
    validate_tender_period_start_date,
    validate_tender_period_duration,
)


class TenderPeriodValidate(object):
    def __init__(self, tender):
        self.context = tender

    def __call__(self, cls, data, period):
        if period:
            if is_new_created(data):
                validate_tender_period_start_date(data, period)
            validate_tender_period_duration(data, period, TENDERING_DURATION)
