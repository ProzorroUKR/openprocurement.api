from schematics.types import BaseType, MD5Type, StringType, URLType
from schematics.types.compound import ModelType

from openprocurement.tender.core.procedure.models.lot import BaseLot, PostBaseLot, TenderLotMixin
from openprocurement.tender.core.procedure.models.period import LotAuctionPeriod
from openprocurement.tender.core.procedure.models.value import BasicValue, EstimatedValue, Value


class CFASelectionPostLot(PostBaseLot):
    guarantee = ModelType(BasicValue)


class CFASelectionPatchLot(BaseLot):
    title = StringType()
    guarantee = ModelType(BasicValue)
    minimalStep = ModelType(Value)
    status = StringType(choices=["active"])


class CFASelectionPostTenderLot(CFASelectionPostLot, TenderLotMixin):
    pass


class CFASelectionPatchTenderLot(BaseLot, TenderLotMixin):
    title = StringType()
    guarantee = ModelType(BasicValue)
    minimalStep = ModelType(Value)


class CFASelectionLot(BaseLot, TenderLotMixin):
    id = MD5Type(required=True)
    value = ModelType(EstimatedValue)
    minimalStep = ModelType(Value)
    guarantee = ModelType(BasicValue)

    auctionPeriod = ModelType(LotAuctionPeriod)
    auctionUrl = URLType()
    numberOfBids = BaseType()  # deprecated
