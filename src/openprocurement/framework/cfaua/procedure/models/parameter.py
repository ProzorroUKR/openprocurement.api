from schematics.types import StringType
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import DecimalType


class Parameter(Model):
    code = StringType(required=True)
    value = DecimalType(required=True)
