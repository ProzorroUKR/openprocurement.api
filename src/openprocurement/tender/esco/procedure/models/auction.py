from pydantic import Field

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
    StringDecimal,
)
from openprocurement.tender.core.procedure.models.auction import (
    AuctionLotResults,
    AuctionResults,
    DecimalWeightedValueResult,
)
from openprocurement.tender.esco.procedure.models.value import ESCOContractDuration


class ESCOValueResult(Model):
    amount: StringDecimal | None = Field(None, ge=0)
    yearlyPaymentsPercentage: StringDecimal | None = Field(None, ge=0)
    contractDuration: ESCOContractDuration | None = None


class ESCOBidResult(Model):
    id: MD5 | None = None
    value: ESCOValueResult | None = None
    weightedValue: DecimalWeightedValueResult | None = None
    date: IsoDateTime | None = None


class ESCOAuctionResults(AuctionResults):
    bids: list[ESCOBidResult]


class ESCOLotResult(Model):
    relatedLot: MD5 | None = None
    value: ESCOValueResult | None = None
    weightedValue: DecimalWeightedValueResult | None = None
    date: IsoDateTime | None = None


class ESCOBidLotResult(Model):
    id: MD5 | None = None
    lotValues: list[ESCOLotResult] | None = None


class ESCOAuctionLotResults(AuctionLotResults):
    bids: list[ESCOBidLotResult]
