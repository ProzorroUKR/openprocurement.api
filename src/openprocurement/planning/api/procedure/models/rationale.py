from schematics.types import StringType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType


class RationaleObject(Model):
    description = StringType(required=True, max_length=2048)
    date = IsoDateTimeType()
