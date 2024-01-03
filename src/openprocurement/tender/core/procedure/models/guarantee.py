from schematics.types import StringType, FloatType, BooleanType
from openprocurement.api.models import DecimalType
from openprocurement.api.procedure.models.guarantee import (
    Guarantee as BaseGuarantee, validate_currency,
)
from openprocurement.tender.core.procedure.context import get_tender


class Guarantee(BaseGuarantee):
    def validate_currency(self, guarantee, currency):
        validate_currency(get_tender(), guarantee, currency)


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

