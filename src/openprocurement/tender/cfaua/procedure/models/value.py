from decimal import Decimal
from typing import Annotated

from pydantic import Field

from openprocurement.api.procedure.models.value import BasicValue
from openprocurement.api.procedure.types import (
    DecimalOf,
)


class CFAUnitPriceValue(BasicValue):
    amount: Annotated[Decimal, DecimalOf(-3)] | None = Field(None, ge=Decimal("0.0"))
    valueAddedTaxIncluded: bool
