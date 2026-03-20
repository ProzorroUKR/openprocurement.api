from schematics.types import StringType, URLType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.value import AmountPercentageValue, BasicValue
from openprocurement.tender.core.procedure.models.lot import (
    BaseLot,
    PostBaseLot,
    TenderLotMixin,
)
from openprocurement.tender.core.procedure.models.period import LotAuctionPeriod


class PostLot(PostBaseLot):
    value = ModelType(AmountPercentageValue, required=True)
    minimalStep = ModelType(AmountPercentageValue)
    guarantee = ModelType(BasicValue)
    # assetValue = ModelType(PostEstimatedValue, required=True)


class PatchLot(BaseLot):
    title = StringType()
    value = ModelType(AmountPercentageValue)
    minimalStep = ModelType(AmountPercentageValue)
    guarantee = ModelType(BasicValue)
    status = StringType(choices=["active"])
    # assetValue = ModelType(EstimatedValue)


class PostTenderLot(PostLot, TenderLotMixin):
    pass


class PatchTenderLot(BaseLot, TenderLotMixin):
    value = ModelType(AmountPercentageValue)
    minimalStep = ModelType(AmountPercentageValue)
    guarantee = ModelType(BasicValue)
    # assetValue = ModelType(EstimatedValue)


class Lot(BaseLot, TenderLotMixin):
    value = ModelType(AmountPercentageValue, required=True)
    minimalStep = ModelType(AmountPercentageValue)
    guarantee = ModelType(BasicValue)
    # assetValue = ModelType(EstimatedValue, required=True)

    auctionPeriod = ModelType(LotAuctionPeriod)
    auctionUrl = URLType()
