from openprocurement.api.models import DecimalType, IsoDateTimeType, ListType, Model
from openprocurement.api.models import Unit as BaseUnit
from schematics.types import BaseType, BooleanType, FloatType, IntType, StringType
from schematics.types.compound import ModelType


class Period(Model):
    startDate = IsoDateTimeType()
    endDate = IsoDateTimeType()
    durationInDays = IntType()


class Unit(BaseUnit):
    name = StringType(required=True)


class BaseRequirement(Model):
    id = StringType(required=True)
    title = StringType(required=True)
    description = StringType()
    dataType = StringType(required=True, choices=["string", "date-time", "number", "integer", "boolean"])
    pattern = StringType()
    period = ModelType(Period)
    unit = ModelType(Unit)


class RequirementString(BaseRequirement):
    minValue = StringType()
    maxValue = StringType()
    expectedValue = StringType()


class RequirementDateTime(BaseRequirement):
    minValue = IsoDateTimeType()
    maxValue = IsoDateTimeType()
    expectedValue = IsoDateTimeType()


class RequirementNumber(BaseRequirement):
    minValue = DecimalType()
    maxValue = DecimalType()
    expectedValue = DecimalType()


class RequirementInteger(BaseRequirement):
    minValue = IntType()
    maxValue = IntType()
    expectedValue = IntType()


class RequirementBoolean(BaseRequirement):
    expectedValue = BooleanType()
