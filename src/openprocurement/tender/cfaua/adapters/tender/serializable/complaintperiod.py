# src/openprocurement.tender.openua/openprocurement/tender/openua/models.py:377
from openprocurement.api.adapters import Serializable
from openprocurement.tender.core.utils import calculate_complaint_business_date
from openprocurement.tender.openua.constants import COMPLAINT_SUBMIT_TIME
from openprocurement.api.models import Period
from schematics.types.compound import ModelType


class SerializableTenderComplaintPeriod(Serializable):
    serialized_name = "complaintPeriod"
    serialized_type = ModelType(Period)

    def __call__(self, obj, *args, **kwargs):
        complaint_period_class = obj._fields["tenderPeriod"]
        end_date = calculate_complaint_business_date(obj.tenderPeriod.endDate, -COMPLAINT_SUBMIT_TIME, obj)
        return complaint_period_class(dict(startDate=obj.tenderPeriod.startDate, endDate=end_date))
