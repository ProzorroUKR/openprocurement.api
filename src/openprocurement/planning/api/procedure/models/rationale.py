from schematics.types import StringType

from openprocurement.api.models import Model, IsoDateTimeType


class RationaleObject(Model):
    description = StringType(required=True, max_length=2048)
    date = IsoDateTimeType()
