from schematics.types import StringType
from openprocurement.tender.core.procedure.models.lot_value import (
    LotValue as BaseLotValue,
    PostLotValue as BasePostLotValue,
    PatchLotValue as BasePatchLotValue,
)


class LotValue(BaseLotValue):
    subcontractingDetails = StringType()


class PostLotValue(BasePostLotValue):
    subcontractingDetails = StringType()


class PatchLotValue(BasePatchLotValue):
    subcontractingDetails = StringType()
