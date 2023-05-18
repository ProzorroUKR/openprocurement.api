from schematics.types.compound import ModelType
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.esco.procedure.models.value import ESCOValue, PatchESCOValue
from openprocurement.tender.esco.procedure.validation import validate_lotvalue_value
from openprocurement.tender.openua.procedure.models.lot_value import (
    PostLotValue as BasePostLotValue,
    PatchLotValue as BasePatchLotValue,
    LotValue as BaseLotValue,
)


class PostLotValue(BasePostLotValue):
    value = ModelType(ESCOValue, required=True)

    def validate_value(self, data, value):
        if data.get("status") != "draft":
            if value is not None:
                validate_lotvalue_value(get_tender(), data["relatedLot"], value)


class PatchLotValue(BasePatchLotValue):
    value = ModelType(PatchESCOValue)

    def validate_value(self, data, value):
        return  # depends on status,  will be validated in LotValue model


class LotValue(BaseLotValue):
    value = ModelType(ESCOValue, required=True)

    def validate_value(self, data, value):
        if data.get("status") != "draft":
            if value is not None:
                validate_lotvalue_value(get_tender(), data["relatedLot"], value)
