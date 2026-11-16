from decimal import Decimal
from typing import Annotated

from pydantic import Field

from openprocurement.api.procedure.models.value import AmountPercentageValue, BasicValue
from openprocurement.api.procedure.types import (
    DecimalOf,
    NormalizedDecimalOf,
)


class Value(BasicValue):
    valueAddedTaxIncluded: bool


class EstimatedValue(Value):
    amount: float | None = Field(None, ge=0)


class PostEstimatedValue(EstimatedValue):
    valueAddedTaxIncluded: bool = False


class WeightedValue(BasicValue):
    amount: Annotated[Decimal, DecimalOf(-2)]
    denominator: float | None = None
    addition: Annotated[Decimal, DecimalOf(-2)] | None = None
    valueAddedTaxIncluded: bool | None = None


class AmountPercentageWeightedValue(AmountPercentageValue):
    amountPercentage: Annotated[Decimal, NormalizedDecimalOf(-3)]
    denominator: float | None = None
    addition: Annotated[Decimal, DecimalOf(-2)] | None = None
