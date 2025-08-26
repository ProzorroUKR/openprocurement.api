from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.procedure.models.lot_value import (
    LotValue as BaseLotValue,
)
from openprocurement.tender.core.procedure.models.lot_value import (
    PatchLotValue as BasePatchLotValue,
)
from openprocurement.tender.core.procedure.models.lot_value import (
    PostLotValue as BasePostLotValue,
)
from openprocurement.tender.core.procedure.validation import validate_lotvalue_value


class PostLotValue(BasePostLotValue):
    def validate_value(self, data, value):
        validate_lotvalue_value(get_tender(), data["relatedLot"], value)


class PatchLotValue(BasePatchLotValue):
    def validate_value(self, data, value):
        validate_lotvalue_value(get_tender(), data["relatedLot"], value)


class LotValue(BaseLotValue):
    def validate_value(self, data, value):
        validate_lotvalue_value(get_tender(), data["relatedLot"], value)
