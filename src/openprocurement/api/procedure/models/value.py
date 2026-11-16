from decimal import Decimal

from pydantic import Field, field_validator

from openprocurement.api.constants import CURRENCIES
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import NormalizedDecimal

MIN_VALUE = Decimal("0")
MAX_VALUE = Decimal("100")
PRECISION = -3


class BasicValue(Model):
    amount: float = Field(ge=0)  # Amount as a number.
    currency: str = Field("UAH", max_length=3, min_length=3)  # 3-letter ISO 4217 format.

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, currency: str) -> str:
        if currency not in CURRENCIES:
            raise ValueError(f"Currency must be only {', '.join(CURRENCIES)}.")
        return currency


class Value(BasicValue):
    valueAddedTaxIncluded: bool = False


class EstimatedValue(Value):
    amount: float | None = Field(None, ge=0)  # type: ignore[assignment]


class ContractValue(Value):
    amountNet: float | None = Field(None, ge=0)


class AmountPercentageValue(Model):
    amountPercentage: NormalizedDecimal = Field(ge=MIN_VALUE, le=MAX_VALUE)
