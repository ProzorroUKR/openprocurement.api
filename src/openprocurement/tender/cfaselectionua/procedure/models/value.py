from schematics.types import FloatType

from openprocurement.api.procedure.models.value import Value as BaseValue


class CFASelectionUnitPriceValue(BaseValue):
    amount = FloatType(min_value=0)
