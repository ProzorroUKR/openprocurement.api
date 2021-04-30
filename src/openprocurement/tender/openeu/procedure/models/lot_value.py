from schematics.types import StringType
from openprocurement.tender.openua.procedure.models.lot_value import (
    LotValue as BaseLotValue,
    PostLotValue as BasePostLotValue,
    PatchLotValue as BasePatchLotValue,
)


class LotValue(BaseLotValue):
    status = StringType(choices=["pending", "active", "unsuccessful"])


class PostLotValue(BasePostLotValue):
    status = StringType(choices=["pending", "active", "unsuccessful"], default="pending")


class PatchLotValue(BasePatchLotValue):
    pass
