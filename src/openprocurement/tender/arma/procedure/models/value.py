from decimal import Decimal

from schematics.types import BooleanType, StringType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import NormalizedDecimalType


class ARMAMinExpectedIncome(Model):
    amount = NormalizedDecimalType(precision=-2, min_value=Decimal("0"), required=True)
    currency = StringType(required=True, default="UAH", choices=["UAH"], max_length=3, min_length=3)
    valueAddedTaxIncluded = BooleanType(required=True)
