from openprocurement.tender.core.procedure.models.lot import (
    BaseLot,
    PatchLot,
    PatchTenderLot,
    PostBaseLot,
    TenderLotMixin,
)
from openprocurement.tender.core.procedure.models.value import EstimatedValue, PostEstimatedValue


class LimitedPostLot(PostBaseLot):
    value: PostEstimatedValue


class LimitedPatchLot(PatchLot):
    title: str | None = None
    value: EstimatedValue | None = None


class LimitedPostTenderLot(LimitedPostLot, TenderLotMixin):
    pass


class LimitedPatchTenderLot(PatchTenderLot, TenderLotMixin):
    value: EstimatedValue


class LimitedLot(BaseLot, TenderLotMixin):
    value: EstimatedValue
