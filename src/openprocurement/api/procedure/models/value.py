from schematics.exceptions import ValidationError
from schematics.types import BooleanType, FloatType, StringType

from openprocurement.api.constants import CURRENCIES
from openprocurement.api.procedure.models.base import Model


class BasicValue(Model):
    amount = FloatType(required=True, min_value=0)  # Amount as a number.
    currency = StringType(required=True, default="UAH", max_length=3, min_length=3)  # 3-letter ISO 4217 format.

    def validate_currency(self, guarantee, currency):
        if currency not in CURRENCIES:
            raise ValidationError(f"Currency must be only {', '.join(CURRENCIES)}.")


class Value(BasicValue):
    valueAddedTaxIncluded = BooleanType(required=True, default=True)


class EstimatedValue(Value):
    amount = FloatType(required=False, min_value=0)


class ContractValue(Value):
    amountNet = FloatType(min_value=0)
