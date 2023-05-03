from schematics.types import StringType

from openprocurement.tender.core.procedure.models.base import ModelType
from openprocurement.tender.core.procedure.models.guarantee import WeightedValue
from openprocurement.tender.core.procedure.models.lot_value import (
    LotValue as BaseLotValue,
    PostLotValue as BasePostLotValue,
    PatchLotValue as BasePatchLotValue,
)


class LotValue(BaseLotValue):
    subcontractingDetails = StringType()
    weightedValue = ModelType(WeightedValue)


class PostLotValue(BasePostLotValue):
    subcontractingDetails = StringType()


class PatchLotValue(BasePatchLotValue):
    subcontractingDetails = StringType()
