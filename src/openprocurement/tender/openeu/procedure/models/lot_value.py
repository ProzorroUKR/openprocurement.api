from openprocurement.tender.openua.procedure.models.lot_value import (
    LotValue as BaseLotValue,
)
from openprocurement.tender.openua.procedure.models.lot_value import (
    PatchLotValue as BasePatchLotValue,
)
from openprocurement.tender.openua.procedure.models.lot_value import (
    PostLotValue as BasePostLotValue,
)


class LotValue(BaseLotValue):
    pass


class PostLotValue(BasePostLotValue):
    pass


class PatchLotValue(BasePatchLotValue):
    pass
