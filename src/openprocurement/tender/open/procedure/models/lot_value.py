from schematics.types import StringType

from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.procedure.models.lot_value import (
    LotValue as BaseLotValue,
    PostLotValue as BasePostLotValue,
    PatchLotValue as BasePatchLotValue,
)
from openprocurement.tender.core.procedure.validation import validate_lotvalue_value


class PostLotValue(BasePostLotValue):
    subcontractingDetails = StringType()

    def validate_value(self, data, value):
        validate_lotvalue_value(get_tender(), data["relatedLot"], value)


class PatchLotValue(BasePatchLotValue):
    subcontractingDetails = StringType()

    def validate_value(self, data, value):
        if value is not None:
            validate_lotvalue_value(get_tender(), data["relatedLot"], value)


class LotValue(BaseLotValue):
    subcontractingDetails = StringType()

    def validate_value(self, data, value):
        validate_lotvalue_value(get_tender(), data["relatedLot"], value)
