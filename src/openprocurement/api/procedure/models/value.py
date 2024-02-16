from schematics.types import BooleanType, FloatType

from openprocurement.api.procedure.models.guarantee import Guarantee
from openprocurement.api.procedure.types import DecimalType


class Value(Guarantee):
    valueAddedTaxIncluded = BooleanType(required=True, default=True)
    denominator = DecimalType()
    addition = DecimalType()


class ContractValue(Value):
    amountNet = FloatType(min_value=0)
