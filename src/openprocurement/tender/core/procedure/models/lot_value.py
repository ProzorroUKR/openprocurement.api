from schematics.types.compound import ModelType
from schematics.types import MD5Type, StringType
from openprocurement.api.models import Model, Value
from openprocurement.tender.core.procedure.validation import (
    validate_lotvalue_value,
    validate_relatedlot,
)
from openprocurement.tender.core.procedure.context import get_tender


class PostLotValue(Model):
    value = ModelType(Value, required=True)
    relatedLot = MD5Type(required=True)

    def validate_value(self, data, value):
        tender = get_tender()
        validate_lotvalue_value(tender, data["relatedLot"], value)

    def validate_relatedLot(self, data, related_lot):
        tender = get_tender()
        validate_relatedlot(tender, related_lot)


class PatchLotValue(PostLotValue):
    value = ModelType(Value)
    relatedLot = MD5Type()

    def validate_value(self, data, value):
        if value is not None:
            super().validate_value(self, data, value)

    def validate_relatedLot(self, data, related_lot):
        if related_lot is not None:
            super().validate_relatedLot(self, data, related_lot)


class LotValue(PostLotValue):
    date = StringType()
