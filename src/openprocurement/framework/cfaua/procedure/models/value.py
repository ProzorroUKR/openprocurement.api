from decimal import Decimal

from openprocurement.api.procedure.models.value import Value as BaseValue
from openprocurement.api.procedure.types import DecimalType


class Value(BaseValue):
    amount = DecimalType(required=True, precision=-2, min_value=Decimal("0.0"))
