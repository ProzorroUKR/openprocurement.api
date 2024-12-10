from schematics.types import StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.tender.core.procedure.models.guarantee import (
    EstimatedValue,
    PostEstimatedValue,
)
from openprocurement.tender.core.procedure.models.lot import BaseLot
from openprocurement.tender.core.procedure.models.lot import PatchLot as BasePatchLot
from openprocurement.tender.core.procedure.models.lot import (
    PatchTenderLot as BasePatchTenderLot,
)
from openprocurement.tender.core.procedure.models.lot import PostBaseLot, TenderLotMixin


class PostLot(PostBaseLot):
    value = ModelType(PostEstimatedValue, required=True)


class PatchLot(BasePatchLot):
    title = StringType()
    value = ModelType(EstimatedValue)


class PostTenderLot(PostLot, TenderLotMixin):
    pass


class PatchTenderLot(BasePatchTenderLot, TenderLotMixin):
    value = ModelType(EstimatedValue, required=True)


class Lot(BaseLot, TenderLotMixin):
    value = ModelType(EstimatedValue, required=True)
