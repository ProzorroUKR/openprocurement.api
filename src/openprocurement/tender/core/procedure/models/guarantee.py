from schematics.exceptions import ValidationError
from schematics.types import StringType, FloatType, BooleanType
from openprocurement.api.models import Model, DecimalType
from openprocurement.tender.core.procedure.utils import tender_created_after
from openprocurement.api.constants import (
    VALIDATE_CURRENCY_FROM,
    CURRENCIES,
)


class Guarantee(Model):
    amount = FloatType(required=True, min_value=0)  # Amount as a number.
    currency = StringType(required=True, max_length=3, min_length=3)  # 3-letter ISO 4217 format.

    def validate_currency(self, data, value):
        if tender_created_after(VALIDATE_CURRENCY_FROM) and value not in CURRENCIES:
            raise ValidationError(f"Currency must be only {', '.join(CURRENCIES)}.")


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

