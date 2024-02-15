from schematics.types import StringType

from openprocurement.tender.core.procedure.models.lot_value import (
    LotValue as BaseLotValue,
)
from openprocurement.tender.core.procedure.models.lot_value import (
    PatchLotValue as BasePatchLotValue,
)
from openprocurement.tender.core.procedure.models.lot_value import (
    PostLotValue as BasePostLotValue,
)


class LotValue(BaseLotValue):
    subcontractingDetails = StringType()


class PostLotValue(BasePostLotValue):
    subcontractingDetails = StringType()


class PatchLotValue(BasePatchLotValue):
    subcontractingDetails = StringType()
