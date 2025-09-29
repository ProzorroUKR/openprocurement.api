from schematics.types import BaseType, MD5Type, StringType, URLType
from schematics.types.compound import ModelType

from openprocurement.tender.core.procedure.models.lot import (
    BaseLot,
    PostBaseLot,
    TenderLotMixin,
)
from openprocurement.tender.core.procedure.models.period import LotAuctionPeriod
from openprocurement.tender.core.procedure.models.value import (
    BasicValue,
    EstimatedValue,
    Value,
)

# -- START model for view ---


class PostLot(PostBaseLot):
    guarantee = ModelType(BasicValue)


class PatchLot(BaseLot):
    title = StringType()
    guarantee = ModelType(BasicValue)
    minimalStep = ModelType(Value)
    status = StringType(choices=["active"])


# -- END models for view ---


class PostTenderLot(PostLot, TenderLotMixin):
    pass


class PatchTenderLot(BaseLot, TenderLotMixin):
    title = StringType()
    guarantee = ModelType(BasicValue)
    minimalStep = ModelType(Value)


class Lot(BaseLot, TenderLotMixin):
    id = MD5Type(required=True)
    value = ModelType(EstimatedValue)
    minimalStep = ModelType(Value)
    guarantee = ModelType(BasicValue)

    auctionPeriod = ModelType(LotAuctionPeriod)
    auctionUrl = URLType()
    numberOfBids = BaseType()  # deprecated
