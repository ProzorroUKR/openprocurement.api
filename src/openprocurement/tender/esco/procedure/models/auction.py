from schematics.types import MD5Type

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType, StringDecimalType
from openprocurement.tender.core.procedure.models.auction import (
    AuctionLotResults,
    AuctionResults,
    DecimalWeightedValueResult,
)
from openprocurement.tender.esco.procedure.models.value import ESCOContractDuration


class ESCOValueResult(Model):
    amount = StringDecimalType(min_value=0)  # this one is going to be
    yearlyPaymentsPercentage = StringDecimalType(min_value=0)
    contractDuration = ModelType(ESCOContractDuration)


class ESCOBidResult(Model):
    id = MD5Type()
    value = ModelType(ESCOValueResult)
    weightedValue = ModelType(DecimalWeightedValueResult)
    date = IsoDateTimeType()


class ESCOAuctionResults(AuctionResults):
    bids = ListType(ModelType(ESCOBidResult, required=True))


class ESCOLotResult(Model):
    relatedLot = MD5Type()
    value = ModelType(ESCOValueResult)
    weightedValue = ModelType(DecimalWeightedValueResult)
    date = IsoDateTimeType()


class ESCOBidLotResult(Model):
    id = MD5Type()
    lotValues = ListType(ModelType(ESCOLotResult, required=True))


class ESCOAuctionLotResults(AuctionLotResults):
    bids = ListType(ModelType(ESCOBidLotResult, required=True), required=True)
