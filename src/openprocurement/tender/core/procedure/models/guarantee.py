from schematics.types import BooleanType, FloatType, StringType

from openprocurement.api.procedure.models.guarantee import Guarantee as BaseGuarantee
from openprocurement.api.procedure.types import DecimalType


class Guarantee(BaseGuarantee):
    pass


class Value(Guarantee):
    valueAddedTaxIncluded = BooleanType(required=True)


class PostGuarantee(Guarantee):
    currency = StringType(required=True, default="UAH", max_length=3, min_length=3)


class PostValue(PostGuarantee, Value):
    valueAddedTaxIncluded = BooleanType(required=True, default=True)


class WeightedValue(PostValue):
    amount = DecimalType(required=True, precision=-2)
    denominator = FloatType()
    addition = DecimalType(precision=-2)
