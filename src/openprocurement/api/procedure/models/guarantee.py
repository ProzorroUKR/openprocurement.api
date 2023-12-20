from schematics.exceptions import ValidationError
from schematics.types import FloatType, StringType

from openprocurement.api.constants import VALIDATE_CURRENCY_FROM, CURRENCIES
from openprocurement.api.models import Model
from openprocurement.api.procedure.utils import is_obj_const_active


class Guarantee(Model):
    amount = FloatType(required=True, min_value=0)  # Amount as a number.
    currency = StringType(required=True, max_length=3, min_length=3)  # 3-letter ISO 4217 format.


def validate_currency(obj, data, value):
    if is_obj_const_active(obj, VALIDATE_CURRENCY_FROM) and value not in CURRENCIES:
        raise ValidationError(f"Currency must be only {', '.join(CURRENCIES)}.")
