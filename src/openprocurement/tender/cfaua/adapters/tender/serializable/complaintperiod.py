# src/openprocurement.tender.openua/openprocurement/tender/openua/models.py:377
from openprocurement.api.adapters import Serializable
from openprocurement.tender.core.utils import calculate_business_date
from openprocurement.tender.openua.constants import COMPLAINT_SUBMIT_TIME
from openprocurement.tender.openua.utils import calculate_normalized_date
from openprocurement.api.models import Period
from schematics.types.compound import ModelType


class SerializableTenderComplaintPeriod(Serializable):
    serialized_name = "complaintPeriod"
    serialized_type = ModelType(Period)

    def __call__(self, obj, *args, **kwargs):
        complaintPeriod_class = obj._fields["tenderPeriod"]
        normalized_end = calculate_normalized_date(obj.tenderPeriod.endDate, obj)
        return complaintPeriod_class(
            dict(
                startDate=obj.tenderPeriod.startDate,
                endDate=calculate_business_date(normalized_end, -COMPLAINT_SUBMIT_TIME, obj),
            )
        )
