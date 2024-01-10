from decimal import Decimal
from schematics.types import StringType, BooleanType
from schematics.types.compound import ModelType
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import DecimalType
from openprocurement.tender.core.procedure.models.guarantee import Guarantee


class Value(Guarantee):
    amount = DecimalType(min_value=Decimal("0.0"))
    valueAddedTaxIncluded = BooleanType(required=True)


class UnitPrice(Model):
    relatedItem = StringType(required=True)
    value = ModelType(Value)
