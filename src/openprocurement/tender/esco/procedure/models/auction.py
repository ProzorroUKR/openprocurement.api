from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import ListType, ModelType, StringDecimalType, IsoDateTimeType
from openprocurement.tender.core.procedure.models.auction import (
    AuctionLotResults as BaseAuctionLotResults,
    AuctionResults as BaseAuctionResults,
)
from openprocurement.tender.esco.procedure.models.value import ContractDuration
from schematics.types import MD5Type

from openprocurement.tender.openeu.procedure.models.auction import WeightedValueResult


# auction results
class ValueResult(Model):
    amount = StringDecimalType(min_value=0)  # this one is going to be
    yearlyPaymentsPercentage = StringDecimalType(min_value=0)
    contractDuration = ModelType(ContractDuration)


class BidResult(Model):
    id = MD5Type()
    value = ModelType(ValueResult)
    weightedValue = ModelType(WeightedValueResult)
    date = IsoDateTimeType()


class AuctionResults(BaseAuctionResults):
    bids = ListType(ModelType(BidResult, required=True))


# auction lot results
class LotResult(Model):
    relatedLot = MD5Type()
    value = ModelType(ValueResult)
    weightedValue = ModelType(WeightedValueResult)
    date = IsoDateTimeType()


class BidLotResult(Model):
    id = MD5Type()
    lotValues = ListType(ModelType(LotResult, required=True))


class AuctionLotResults(BaseAuctionLotResults):
    bids = ListType(ModelType(BidLotResult, required=True), required=True)
