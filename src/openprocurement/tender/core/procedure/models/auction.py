from decimal import Decimal
from itertools import zip_longest
from typing import Annotated

from pydantic import Field, field_validator

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    MD5,
    DecimalOf,
    IsoDateTime,
    Url,
)
from openprocurement.tender.core.procedure.context import get_request


class LotAuctionUrl(Model):
    id: MD5 | None = None
    auctionUrl: Url | None = None


class ParticipationUrl(Model):
    id: MD5 | None = None
    participationUrl: Url | None = None


class LotValueUrl(Model):
    relatedLot: MD5 | None = None
    participationUrl: Url | None = None


class AuctionUrls(Model):
    auctionUrl: Url | None = None
    bids: list[ParticipationUrl]

    @field_validator("bids")
    @classmethod
    def validate_bids(cls, bids):
        """
        example input
        "bids": [{}, {"participationUrl": "http://..."}, {}]
        """
        bid_ids = [b["id"] for b in get_tender().get("bids", "")]
        passed_ids = []
        for bid, positional_bid_id in zip_longest(bids, bid_ids):
            if None in (positional_bid_id, bid):
                raise ValidationError("Number of bids did not match the number of tender bids")
            if bid.id is None:
                bid.id = positional_bid_id
            passed_ids.append(bid.id)
        if passed_ids != bid_ids:
            raise ValidationError("Auction bids should be identical to the tender bids")
        return bids


class BidLotValue(Model):
    id: MD5 | None = None
    lotValues: list[LotValueUrl] | None = None


class LotAuctionUrls(Model):
    lots: list[LotAuctionUrl]
    bids: list[BidLotValue]

    @field_validator("lots")
    @classmethod
    def validate_lots(cls, lots):
        """
        example input
        "lots": [{}, {"auctionUrl": "http://auction.."}, {}]
        """
        lot_id = get_request().matchdict.get("auction_lot_id")
        lot_ids = [lot["id"] for lot in get_tender().get("lots", "")]
        passed_ids = []
        for lot, positional_lot_id in zip_longest(lots, lot_ids):
            if None in (positional_lot_id, lot):
                raise ValidationError("Number of lots did not match the number of tender lots")
            if lot.id is None:
                lot.id = positional_lot_id
            if lot.id == lot_id:
                if lot.auctionUrl is None:
                    raise ValidationError("Auction url required")
            else:
                for f in type(lot).model_fields:
                    if f != "id":
                        setattr(lot, f, None)
            passed_ids.append(lot.id)
        if passed_ids != lot_ids:
            raise ValidationError("Auction lots should be identical to the tender lots")
        return lots

    @field_validator("bids")
    @classmethod
    def validate_bids(cls, bids):
        """
        example input
        "bids": [{}, {"lotValues": [{}, {"participationUrl": "http://..."}, {}]}, {}]
        """
        lot_id = get_request().matchdict.get("auction_lot_id")
        bid_ids = [b["id"] for b in get_tender().get("bids", "")]
        tender_bids = {b["id"]: b for b in get_tender().get("bids", "")}
        passed_ids = []
        for bid, positional_bid_id in zip_longest(bids, bid_ids):
            if None in (positional_bid_id, bid):
                raise ValidationError("Number of auction results did not match the number of tender bids")
            if bid.id is None:
                bid.id = positional_bid_id
            elif bid.id not in tender_bids:
                raise ValidationError("Auction bids should be identical to the tender bids")
            passed_ids.append(bid.id)
            if bid.lotValues:
                passed_related_lots = []
                tender_related_lots = [v["relatedLot"] for v in tender_bids[bid.id]["lotValues"]]
                for value, positional_related_lot in zip_longest(bid.lotValues, tender_related_lots):
                    if positional_related_lot is None:
                        raise ValidationError(
                            "Number of lots of auction results did not match the number of tender lots"
                        )
                    if value is None:
                        continue
                    if value.relatedLot is None:
                        value.relatedLot = positional_related_lot
                    if value.relatedLot == lot_id:
                        if value.participationUrl is None:
                            raise ValidationError("Auction participation url required")
                    else:
                        for f in type(value).model_fields:
                            if f != "relatedLot":
                                setattr(value, f, None)
                    passed_related_lots.append(value.relatedLot)
                if passed_related_lots != tender_related_lots[: len(passed_related_lots)]:
                    raise ValidationError("Auction bid.lotValues should be identical to the tender bid.lotValues")
        if passed_ids != bid_ids:
            raise ValidationError("Auction bids should be identical to the tender bids")
        return bids


class ValueResult(Model):
    amount: float | None = Field(None, ge=0)
    date: IsoDateTime | None = None
    currency: str | None = None
    valueAddedTaxIncluded: bool | None = None


class WeightedValueResult(Model):
    amount: float | None = Field(None, ge=0)
    date: IsoDateTime | None = None
    currency: str | None = None
    valueAddedTaxIncluded: bool | None = None


class BidResult(Model):
    id: MD5 | None = None
    value: ValueResult | None = None
    weightedValue: WeightedValueResult | None = None
    date: IsoDateTime | None = None


class AuctionResults(Model):
    bids: list[BidResult]

    @field_validator("bids")
    @classmethod
    def validate_bids(cls, bids):
        """
        example input
        "bids": [{}, {"value": 1, "date": "2020-..."}, {}]
        """
        bid_ids = [b["id"] for b in get_tender().get("bids", "")]
        passed_ids = []
        for bid, positional_bid_id in zip_longest(bids, bid_ids):
            if None in (positional_bid_id, bid):
                raise ValidationError("Number of auction results did not match the number of tender bids")
            if bid.id is None:
                bid.id = positional_bid_id
            passed_ids.append(bid.id)
        if passed_ids != bid_ids:
            raise ValidationError("Auction bids should be identical to the tender bids")
        return bids


class LotResult(Model):
    relatedLot: MD5 | None = None
    value: ValueResult | None = None
    weightedValue: WeightedValueResult | None = None
    date: IsoDateTime | None = None


class BidLotResult(Model):
    id: MD5 | None = None
    lotValues: list[LotResult] | None = None


class AuctionLotResults(Model):
    bids: list[BidLotResult]

    @field_validator("bids")
    @classmethod
    def validate_bids(cls, bids):
        """
        example input
        "bids": [{}, {"lotValues": [{}, {"value": 23, "date": "..."}, {}]}, {}]
        """
        lot_id = get_request().matchdict.get("auction_lot_id")
        bid_ids = [b["id"] for b in get_tender().get("bids", "")]
        tender_bids = {b["id"]: b for b in get_tender().get("bids", "")}
        passed_ids = []
        for bid, positional_bid_id in zip_longest(bids, bid_ids):
            if None in (positional_bid_id, bid):
                raise ValidationError("Number of auction results did not match the number of tender bids")
            if bid.id is None:
                bid.id = positional_bid_id
            elif bid.id not in tender_bids:
                raise ValidationError("Auction bids should be identical to the tender bids")
            passed_ids.append(bid.id)
            if bid.lotValues:
                passed_related_lots = []
                tender_related_lots = [v["relatedLot"] for v in tender_bids[bid.id]["lotValues"]]
                for value, positional_related_lot in zip_longest(bid.lotValues, tender_related_lots):
                    if positional_related_lot is None:
                        raise ValidationError(
                            "Number of lots of auction results did not match the number of tender lots"
                        )
                    if value is None:
                        continue
                    if value.relatedLot is None:
                        value.relatedLot = positional_related_lot
                    passed_related_lots.append(value.relatedLot)
                    if value.relatedLot != lot_id:
                        for f in type(value).model_fields:
                            if f != "relatedLot":
                                setattr(value, f, None)
                if passed_related_lots != tender_related_lots[: len(passed_related_lots)]:
                    raise ValidationError("Auction bid.lotValues should be identical to the tender bid.lotValues")
        if passed_ids != bid_ids:
            raise ValidationError("Auction bids should be identical to the tender bids")
        return bids


class AuctionPeriodStartDate(Model):
    startDate: IsoDateTime | None = None


class DecimalWeightedValueResult(WeightedValueResult):
    amount: Annotated[Decimal, DecimalOf(-2)] | None = Field(None, ge=0)


class DecimalBidResult(BidResult):
    weightedValue: DecimalWeightedValueResult | None = None


class DecimalAuctionResults(AuctionResults):
    bids: list[DecimalBidResult]


class DecimalLotResult(LotResult):
    weightedValue: DecimalWeightedValueResult | None = None


class DecimalBidLotResult(BidLotResult):
    lotValues: list[DecimalLotResult] | None = None


class DecimalAuctionLotResults(AuctionLotResults):
    bids: list[DecimalBidLotResult]
