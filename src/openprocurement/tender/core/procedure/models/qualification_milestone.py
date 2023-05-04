from openprocurement.tender.core.utils import calculate_tender_date, calculate_complaint_business_date
from openprocurement.tender.core.procedure.models.base import Model, ListType, ModelType
from openprocurement.tender.core.procedure.context import get_request, get_tender
from openprocurement.api.context import get_now
from openprocurement.api.models import IsoDateTimeType
from schematics.types.serializable import serializable
from schematics.exceptions import ValidationError
from schematics.types import URLType, MD5Type, FloatType, StringType, BooleanType
from itertools import zip_longest
from datetime import timedelta
from enum import Enum
from uuid import uuid4


class QualificationMilestoneCodes(Enum):
    CODE_24_HOURS = "24h"
    CODE_LOW_PRICE = "alp"


class PostQualificationMilestone(Model):
    code = StringType(
        required=True,
        choices=[
            QualificationMilestoneCodes.CODE_24_HOURS.value,
            # QualificationMilestoneCodes.CODE_LOW_PRICE.value,  # this one cannot be posted
        ]
    )
    description = StringType()

    @serializable
    def id(self):
        return uuid4().hex

    @serializable
    def dueDate(self):
        if self.code == QualificationMilestoneCodes.CODE_24_HOURS.value:
            dt = calculate_tender_date(get_now(), timedelta(hours=24), get_tender())
        elif self.code == QualificationMilestoneCodes.CODE_LOW_PRICE.value:
            dt = calculate_complaint_business_date(get_now(), timedelta(days=1), get_tender(), working_days=True)
        else:
            raise NotImplementedError(f"Unexpected code {self.code}")
        return dt.isoformat()

    @serializable
    def date(self):
        return get_now().isoformat()


# class QualificationMilestone(Model):
#     id = MD5Type(required=True)
#     code = StringType(
#         required=True,
#         choices=[QualificationMilestoneCodes.CODE_24_HOURS.value,
#                  QualificationMilestoneCodes.CODE_LOW_PRICE.value]
#     )
#     dueDate = IsoDateTimeType(required=True)
#     date = IsoDateTimeType(required=True)
#     description = StringType()
