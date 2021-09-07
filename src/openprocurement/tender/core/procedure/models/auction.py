from openprocurement.tender.core.procedure.models.base import Model, ListType, ModelType
from openprocurement.tender.core.procedure.context import get_request, get_tender
from openprocurement.api.models import IsoDateTimeType
from schematics.exceptions import ValidationError
from schematics.types import URLType, MD5Type, FloatType, StringType, BooleanType
from itertools import zip_longest


# set urls
class LotAuctionUrl(Model):
    id = MD5Type()
    auctionUrl = URLType()


class ParticipationUrl(Model):
    id = MD5Type()
    participationUrl = URLType()  # required ?


class LotValueUrl(Model):
    relatedLot = MD5Type()
    participationUrl = URLType()


class AuctionUrls(Model):
    auctionUrl = URLType()  # required ?
    bids = ListType(ModelType(ParticipationUrl, required=True))

    def validate_bids(self, _, bids):
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
                # For now we allow to skip passing id of update object
                # Also empty objects {} do not appear in result when we call serialise() method
                # there is a way to hack schematics to do so (see def openprocurement.api.Model.to_patch)
                # but I don't want to stick to this version of schematics and to any version of it
            passed_ids.append(bid.id)

        if passed_ids != bid_ids:
            raise ValidationError("Auction bids should be identical to the tender bids")
        return bids


class BidLotValue(Model):
    id = MD5Type()
    lotValues = ListType(ModelType(LotValueUrl, required=True))  # optional? bid may be cancelled or something..


class LotAuctionUrls(Model):
    # auctionUrl = URLType()
    lots = ListType(ModelType(LotAuctionUrl, required=True), required=True)
    bids = ListType(ModelType(BidLotValue, required=True), required=True)

    def validate_lots(self, _, lots):
        """
        example input
        "lots": [{}, {"auctionUrl": "http://auction.."}, {}]
        """
        lot_id = get_request().matchdict.get("auction_lot_id")
        lot_ids = [l["id"] for l in get_tender().get("lots", "")]
        passed_ids = []
        for lot, positional_lot_id in zip_longest(lots, lot_ids):
            if None in (positional_lot_id, lot):
                raise ValidationError("Number of lots did not match the number of tender lots")
            if lot.id is None:
                lot.id = positional_lot_id
                # For now we allow to skip passing id of update object
                # Also empty objects {} do not appear in result when we call serialise() method
                # there is a way to hack schematics to do so (see def openprocurement.api.Model.to_patch)
                # but I don't want to stick to this version of schematics and to any version of it

            if lot.id == lot_id:
                if lot.auctionUrl is None:
                    raise ValidationError("Auction url required")
            else: # post to /auctions/{lot_id} updates only related lots
                for f in lot:
                    if f != "id":
                        lot[f] = None

            passed_ids.append(lot.id)

        if passed_ids != lot_ids:
            raise ValidationError("Auction lots should be identical to the tender lots")
        return lots

    def validate_bids(self, _, bids):
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
                # For now we allow to skip passing id of update object
                # Also empty objects {} do not appear in result when we call serialise() method
                # there is a way to hack schematics to do so (see def openprocurement.api.Model.to_patch)
                # but I don't want to stick to this version of schematics and to any version of it
            passed_ids.append(bid.id)

            # lotValues check ---
            if bid.lotValues:
                passed_related_lots = []
                tender_related_lots = [v["relatedLot"] for v in tender_bids[bid.id]["lotValues"]]
                for value, positional_related_lot in zip_longest(bid.lotValues, tender_related_lots):
                    if positional_related_lot is None:
                        raise ValidationError(
                            "Number of lots of auction results did not match the number of tender lots")
                    if value is None:  # passed list actually can be shorter
                        continue

                    if value.relatedLot is None:
                        value.relatedLot = positional_related_lot

                    if value.relatedLot == lot_id:
                        if value.participationUrl is None:
                            raise ValidationError("Auction participation url required")

                    else:   # post to /auctions/{lot_id} updates only related lotValues
                        for f in value:
                            if f != "relatedLot":
                                value[f] = None

                    passed_related_lots.append(value.relatedLot)

                if passed_related_lots != tender_related_lots[:len(passed_related_lots)]:  # passed can be shorter
                    raise ValidationError("Auction bid.lotValues should be identical to the tender bid.lotValues")
            # -- lotValues check

        if passed_ids != bid_ids:
            raise ValidationError("Auction bids should be identical to the tender bids")
        return bids


# auction results
class ValueResult(Model):
    amount = FloatType(min_value=0)
    date = IsoDateTimeType()

    # these two required by tests and maybe "old" auctions  TODO: rm them after new auctions
    currency = StringType()
    valueAddedTaxIncluded = BooleanType()


class WeightedValueResult(Model):
    amount = FloatType(min_value=0)
    date = IsoDateTimeType()

    # these two required by tests and maybe "old" auctions TODO: rm them after new auctions
    currency = StringType()
    valueAddedTaxIncluded = BooleanType()


class BidResult(Model):
    id = MD5Type()
    value = ModelType(ValueResult)
    weightedValue = ModelType(WeightedValueResult)
    date = IsoDateTimeType()


class AuctionResults(Model):
    bids = ListType(ModelType(BidResult, required=True))

    def validate_bids(self, _, bids):
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
                # For now we allow to skip passing id of update object
                # Also empty objects {} do not appear in result when we call serialise() method
                # there is a way to hack schematics to do so (see def openprocurement.api.Model.to_patch)
                # but I don't want to stick to this version of schematics and to any version of it
            passed_ids.append(bid.id)

        if passed_ids != bid_ids:
            raise ValidationError("Auction bids should be identical to the tender bids")
        return bids


# auction lot results
class LotResult(Model):
    relatedLot = MD5Type()
    value = ModelType(ValueResult)
    weightedValue = ModelType(WeightedValueResult)
    date = IsoDateTimeType()


class BidLotResult(Model):
    id = MD5Type()
    lotValues = ListType(ModelType(LotResult, required=True))


class AuctionLotResults(Model):
    bids = ListType(ModelType(BidLotResult, required=True), required=True)

    def validate_bids(self, _, bids):
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
                # For now we allow to skip passing id of update object
                # Also empty objects {} do not appear in result when we call serialise() method
                # there is a way to hack schematics to do so (see def openprocurement.api.Model.to_patch)
                # but I don't want to stick to this version of schematics and to any version of it
            passed_ids.append(bid.id)

            # lotValues check ---
            if bid.lotValues:
                passed_related_lots = []
                tender_related_lots = [v["relatedLot"] for v in tender_bids[bid.id]["lotValues"]]
                for value, positional_related_lot in zip_longest(bid.lotValues, tender_related_lots):
                    if positional_related_lot is None:
                        raise ValidationError(
                            "Number of lots of auction results did not match the number of tender lots")
                    if value is None:  # passed list actually can be shorter
                        continue

                    if value.relatedLot is None:
                        value.relatedLot = positional_related_lot
                    passed_related_lots.append(value.relatedLot)

                    # patch to /auctions/{lot_id} updates only related lotValues
                    if value.relatedLot != lot_id:
                        for f in value:
                            if f != "relatedLot":
                                value[f] = None

                if passed_related_lots != tender_related_lots[:len(passed_related_lots)]:  # passed can be shorter
                    raise ValidationError("Auction bid.lotValues should be identical to the tender bid.lotValues")
            # -- lotValues check

        if passed_ids != bid_ids:
            raise ValidationError("Auction bids should be identical to the tender bids")
        return bids
