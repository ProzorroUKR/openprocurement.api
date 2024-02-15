from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import Value
from openprocurement.tender.core.procedure.models.guarantee import WeightedValue
from openprocurement.tender.core.procedure.validation import (
    validate_lotvalue_value,
    validate_related_lot,
)


class PostLotValue(Model):
    status = StringType(choices=["pending"], default="pending", required=True)
    value = ModelType(Value, required=True)
    relatedLot = MD5Type(required=True)

    def validate_value(self, data, value):
        validate_lotvalue_value(get_tender(), data["relatedLot"], value)

    def validate_relatedLot(self, data, related_lot):
        validate_related_lot(get_tender(), related_lot)


class PatchLotValue(PostLotValue):
    status = StringType(choices=["pending"], default="pending")
    value = ModelType(Value)
    relatedLot = MD5Type()

    def validate_value(self, data, value):
        if value is not None:
            validate_lotvalue_value(get_tender(), data["relatedLot"], value)

    def validate_relatedLot(self, data, related_lot):
        if related_lot is not None:
            validate_related_lot(get_tender(), related_lot)


class LotValue(PostLotValue):
    weightedValue = ModelType(WeightedValue)
    status = StringType(choices=["pending", "active", "unsuccessful"], required=True)
    date = StringType()
