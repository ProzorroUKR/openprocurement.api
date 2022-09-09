from schematics.exceptions import ValidationError
from schematics.types import StringType, FloatType, BooleanType
from openprocurement.api.utils import get_now
from openprocurement.api.models import Model, DecimalType
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.utils import get_first_revision_date
from openprocurement.api.constants import (
    VALIDATE_CURRENCY_FROM,
    CURRENCIES,
)


class Guarantee(Model):
    amount = FloatType(required=True, min_value=0)  # Amount as a number.
    currency = StringType(required=True, max_length=3, min_length=3)  # 3-letter ISO 4217 format.

    def validate_currency(self, data, value):
        is_valid_date = get_first_revision_date(get_tender(), default=get_now()) >= VALIDATE_CURRENCY_FROM
        if is_valid_date and value not in CURRENCIES:
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

