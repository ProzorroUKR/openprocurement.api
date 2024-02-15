from schematics.types import FloatType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.context import get_contract
from openprocurement.api.procedure.models.base import Model


class Value(Model):
    amount = FloatType(required=True, min_value=0)  # Amount as a number.

    @serializable
    def valueAddedTaxIncluded(self):
        contract = get_contract()
        return contract["value"]["valueAddedTaxIncluded"]

    @serializable
    def currency(self):
        contract = get_contract()
        return contract["value"]["currency"]
