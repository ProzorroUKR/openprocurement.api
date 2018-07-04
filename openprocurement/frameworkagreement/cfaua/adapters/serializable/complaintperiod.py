# src/openprocurement.tender.openua/openprocurement/tender/openua/models.py:377
from openprocurement.tender.core.utils import calculate_business_date
from openprocurement.tender.openua.constants import COMPLAINT_SUBMIT_TIME
from openprocurement.tender.openua.utils import calculate_normalized_date


class TenderComplaintPeriod(object):
    def __init__(self, tender):
        self.context = tender

    def __call__(self, *args, **kwargs):
        complaintPeriod_class = self.context._fields['tenderPeriod']
        normalized_end = calculate_normalized_date(self.context.tenderPeriod.endDate, self.context)
        return complaintPeriod_class(dict(
            startDate=self.context.tenderPeriod.startDate,
            endDate=calculate_business_date(normalized_end, -COMPLAINT_SUBMIT_TIME, self.context)
        ))
