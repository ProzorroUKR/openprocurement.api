from schematics.types import BooleanType

from openprocurement.api.procedure.models.value import ContractValue


class AmountPaid(ContractValue):
    valueAddedTaxIncluded = BooleanType()
