from schematics.types import MD5Type
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType, ListType


class AuctionPeriod(Model):
    startDate = IsoDateTimeType()


class LotData(Model):
    auctionPeriod = ModelType(AuctionPeriod, serialize_when_none=True)


class TenderChronographData(Model):
    _id = MD5Type(deserialize_from=["id"])
    auctionPeriod = ModelType(AuctionPeriod)
    lots = ListType(ModelType(LotData))
