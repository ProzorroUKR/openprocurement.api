from schematics.types import StringType

from openprocurement.tender.core.procedure.models.lot_value import (
    LotValue as BaseLotValue,
)
from openprocurement.tender.core.procedure.models.lot_value import (
    PostLotValue as BasePostLotValue,
)


class PostLotValue(BasePostLotValue):
    subcontractingDetails = StringType()


class LotValue(BaseLotValue):
    subcontractingDetails = StringType()
