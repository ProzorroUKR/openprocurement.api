from schematics.types import FloatType, StringType
from schematics.types.compound import ModelType
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import Value as BaseValue


class Value(BaseValue):
    amount = FloatType(min_value=0)

    def validate_amount(self, data, amount):
        pass


class UnitPrice(Model):
    relatedItem = StringType()
    value = ModelType(Value)

    def validate_relatedItem(self, data, relatedItem):
        pass
