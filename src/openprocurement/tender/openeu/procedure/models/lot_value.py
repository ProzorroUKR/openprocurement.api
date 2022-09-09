from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.tender.core.procedure.models.guarantee import WeightedValue
from openprocurement.tender.openua.procedure.models.lot_value import (
    LotValue as BaseLotValue,
    PostLotValue as BasePostLotValue,
    PatchLotValue as BasePatchLotValue,
)


class LotValue(BaseLotValue):
    status = StringType(choices=["pending", "active", "unsuccessful"], required=True)
    weightedValue = ModelType(WeightedValue)


class PostLotValue(BasePostLotValue):
    status = StringType(choices=["pending", "active"], default="pending")


class PatchLotValue(BasePatchLotValue):
    status = StringType(choices=["pending", "active"], default="pending")
