from schematics.exceptions import ValidationError
from schematics.types import FloatType, StringType

from openprocurement.api.constants import CURRENCIES
from openprocurement.api.procedure.models.base import Model


class Guarantee(Model):
    amount = FloatType(required=True, min_value=0)  # Amount as a number.
    currency = StringType(required=True, default="UAH", max_length=3, min_length=3)  # 3-letter ISO 4217 format.

    def validate_currency(self, guarantee, currency):
        if currency not in CURRENCIES:
            raise ValidationError(f"Currency must be only {', '.join(CURRENCIES)}.")
