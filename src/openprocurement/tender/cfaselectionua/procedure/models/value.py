from pydantic import Field

from openprocurement.api.procedure.models.value import Value as BaseValue


class CFASelectionUnitPriceValue(BaseValue):
    amount: float | None = Field(None, ge=0)
