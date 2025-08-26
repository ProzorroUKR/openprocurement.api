from schematics.types.compound import ModelType

from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.procedure.models.lot_value import (
    LotValue as BaseLotValue,
)
from openprocurement.tender.core.procedure.models.lot_value import (
    PostLotValue as BasePostLotValue,
)
from openprocurement.tender.esco.procedure.models.value import ESCOValue
from openprocurement.tender.esco.procedure.validation import validate_lotvalue_value


class PostLotValue(BasePostLotValue):
    value = ModelType(ESCOValue, required=True)

    def validate_value(self, data, value):
        if data.get("status") != "draft":
            if value is not None:
                validate_lotvalue_value(get_tender(), data["relatedLot"], value)


class PatchLotValue(BasePostLotValue):
    value = ModelType(ESCOValue, required=True)

    def validate_value(self, data, value):
        if data.get("status") != "draft":
            if value is not None:
                validate_lotvalue_value(get_tender(), data["relatedLot"], value)


class LotValue(BaseLotValue):
    value = ModelType(ESCOValue, required=True)

    def validate_value(self, data, value):
        if data.get("status") != "draft":
            if value is not None:
                validate_lotvalue_value(get_tender(), data["relatedLot"], value)
