from schematics.types.compound import ModelType

from openprocurement.api.models import DecimalType, ListType
from openprocurement.tender.core.procedure.models.auction import (
    WeightedValueResult as BaseWeightedValueResult,
    BidResult as BaseBidResult,
    AuctionResults as BaseAuctionResults,
    LotResult as BaseLotResult,
    BidLotResult as BaseBidLotResult,
    AuctionLotResults as BaseAuctionLotResults
)


class WeightedValueResult(BaseWeightedValueResult):
    amount = DecimalType(min_value=0, precision=-2)


class BidResult(BaseBidResult):
    weightedValue = ModelType(WeightedValueResult)


class AuctionResults(BaseAuctionResults):
    bids = ListType(ModelType(BidResult, required=True))


# auction lot results
class LotResult(BaseLotResult):
    weightedValue = ModelType(WeightedValueResult)


class BidLotResult(BaseBidLotResult):
    lotValues = ListType(ModelType(LotResult, required=True))


class AuctionLotResults(BaseAuctionLotResults):
    bids = ListType(ModelType(BidLotResult, required=True), required=True)
