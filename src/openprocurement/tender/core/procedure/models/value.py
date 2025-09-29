from schematics.types import BooleanType, FloatType

from openprocurement.api.procedure.models.value import BasicValue
from openprocurement.api.procedure.types import DecimalType


class Value(BasicValue):
    valueAddedTaxIncluded = BooleanType(required=True)


class EstimatedValue(Value):
    amount = FloatType(required=False, min_value=0)


class PostEstimatedValue(EstimatedValue):
    valueAddedTaxIncluded = BooleanType(required=True, default=True)


class WeightedValue(Value):
    amount = DecimalType(required=True, precision=-2)
    denominator = FloatType()
    addition = DecimalType(precision=-2)
    valueAddedTaxIncluded = BooleanType(required=True, default=True)
