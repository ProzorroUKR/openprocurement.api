from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.tender.core.procedure.models.lot import (
    BaseLot,
    PatchLot,
    PatchTenderLot,
    PostBaseLot,
    TenderLotMixin,
)
from openprocurement.tender.core.procedure.models.value import EstimatedValue, PostEstimatedValue


class LimitedPostLot(PostBaseLot):
    value = ModelType(PostEstimatedValue, required=True)


class LimitedPatchLot(PatchLot):
    title = StringType()
    value = ModelType(EstimatedValue)


class LimitedPostTenderLot(LimitedPostLot, TenderLotMixin):
    pass


class LimitedPatchTenderLot(PatchTenderLot, TenderLotMixin):
    value = ModelType(EstimatedValue, required=True)


class LimitedLot(BaseLot, TenderLotMixin):
    value = ModelType(EstimatedValue, required=True)
