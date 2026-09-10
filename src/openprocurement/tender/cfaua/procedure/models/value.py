from decimal import Decimal

from schematics.types import BooleanType

from openprocurement.api.procedure.models.value import BasicValue
from openprocurement.api.procedure.types import DecimalType


class CFAUnitPriceValue(BasicValue):
    amount = DecimalType(min_value=Decimal("0.0"))
    valueAddedTaxIncluded = BooleanType(required=True)
