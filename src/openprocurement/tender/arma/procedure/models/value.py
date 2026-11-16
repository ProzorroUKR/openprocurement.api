from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    NormalizedDecimalOf,
)


class ARMAMinExpectedIncome(Model):
    amount: Annotated[Decimal, NormalizedDecimalOf(-2)] = Field(ge=Decimal("0"))
    currency: Literal["UAH"] = Field("UAH", min_length=3, max_length=3)
    valueAddedTaxIncluded: bool
