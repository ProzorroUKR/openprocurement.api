from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.models.base import Model, ListType, NoneAllowedModelType
from openprocurement.api.models import IsoDateTimeType
from schematics.types import MD5Type
from schematics.exceptions import ValidationError


class AuctionPeriod(Model):
    startDate = IsoDateTimeType()


class LotData(Model):
    auctionPeriod = NoneAllowedModelType(AuctionPeriod)


class TenderChronographData(Model):
    id = MD5Type()
    auctionPeriod = NoneAllowedModelType(AuctionPeriod)
    lots = ListType(NoneAllowedModelType(LotData))

    def validate_auctionPeriod(self, data, period):
        if period:
            tender = get_tender()
            if tender.get("lots"):
                raise ValidationError("Auction url at tender lvl forbidden")
