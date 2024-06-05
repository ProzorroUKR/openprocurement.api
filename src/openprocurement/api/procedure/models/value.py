from schematics.types import BooleanType, FloatType

from openprocurement.api.procedure.models.guarantee import Guarantee
from openprocurement.api.procedure.types import DecimalType


class Value(Guarantee):
    valueAddedTaxIncluded = BooleanType(required=True, default=True)
    denominator = DecimalType()
    addition = DecimalType()


class EstimatedValue(Value):
    """Estimated tender value.

    Amount is not required.
    """

    amount = FloatType(required=False, min_value=0)


class ContractValue(Value):
    amountNet = FloatType(min_value=0)
