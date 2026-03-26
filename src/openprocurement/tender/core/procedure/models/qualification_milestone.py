from enum import StrEnum
from uuid import uuid4

from schematics.types import StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType


class QualificationMilestoneCode(StrEnum):
    CODE_24_HOURS = "24h"
    CODE_LOW_PRICE = "alp"


class PostQualificationMilestone(Model):
    code = StringType(
        required=True,
        choices=[
            QualificationMilestoneCode.CODE_24_HOURS.value,
            # QualificationMilestoneCode.CODE_LOW_PRICE.value,  # this one cannot be posted
        ],
    )
    description = StringType()
    dueDate = IsoDateTimeType()

    @serializable
    def id(self):
        return uuid4().hex

    @serializable
    def date(self):
        return get_request_now().isoformat()


# class QualificationMilestone(Model):
#     id = MD5Type(required=True)
#     code = StringType(
#         required=True,
#         choices=[QualificationMilestoneCode.CODE_24_HOURS.value,
#                  QualificationMilestoneCode.CODE_LOW_PRICE.value]
#     )
#     dueDate = IsoDateTimeType(required=True)
#     date = IsoDateTimeType(required=True)
#     description = StringType()
