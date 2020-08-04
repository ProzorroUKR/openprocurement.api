from schematics.types import BaseType, BooleanType, FloatType, IntType, StringType, BaseType
from schematics.types.compound import ModelType
from schematics.exceptions import ValidationError

from openprocurement.api.models import DecimalType, IsoDateTimeType, ListType, Model
from openprocurement.api.models import Unit as BaseUnit
from openprocurement.tender.core.validation import validate_value_type


class Unit(BaseUnit):
    name = StringType(required=True)


class Requirement(Model):
    id = StringType(required=True)
    title = StringType(required=True)
    description = StringType()
    dataType = StringType(required=True,
                          choices=["string", "number", "integer", "boolean"])
    unit = ModelType(Unit)
    minValue = StringType()
    maxValue = StringType()
    expectedValue = StringType()

    def validate_minValue(self, data, value):
        validate_value_type(value, data['dataType'])

    def validate_maxValue(self, data, value):
        validate_value_type(value, data['dataType'])

    def validate_expectedValue(self, data, value):
        validate_value_type(value, data['dataType'])
