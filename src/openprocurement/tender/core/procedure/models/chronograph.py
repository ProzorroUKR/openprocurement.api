from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import ListType, IsoDateTimeType
from schematics.types.compound import ModelType
from schematics.types import MD5Type
from schematics.exceptions import ValidationError


class AuctionPeriod(Model):
    startDate = IsoDateTimeType()


class LotData(Model):
    auctionPeriod = ModelType(AuctionPeriod, serialize_when_none=True)


class TenderChronographData(Model):
    _id = MD5Type(deserialize_from=['id'])
    auctionPeriod = ModelType(AuctionPeriod)
    lots = ListType(ModelType(LotData))

    def validate_auctionPeriod(self, data, period):
        if period:
            tender = get_tender()
            if tender.get("lots"):
                raise ValidationError("Auction url at tender lvl forbidden")
