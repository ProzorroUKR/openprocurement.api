from decimal import Decimal
from typing import Annotated

from pydantic import Field

from openprocurement.api.procedure.models.value import Value as BaseValue
from openprocurement.api.procedure.types import (
    DecimalOf,
)


class Value(BaseValue):
    amount: Annotated[Decimal, DecimalOf(-2)] = Field(ge=Decimal("0.0"))
