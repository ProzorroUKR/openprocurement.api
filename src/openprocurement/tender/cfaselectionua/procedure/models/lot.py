from schematics.types import BaseType, MD5Type, StringType, URLType
from schematics.types.compound import ModelType
from schematics.validate import ValidationError

from openprocurement.tender.core.procedure.models.guarantee import Guarantee, Value
from openprocurement.tender.core.procedure.models.lot import (
    BaseLot,
    LotGuaranteeSerializerMixin,
    PostBaseLot,
    TenderLotMixin,
)
from openprocurement.tender.core.procedure.models.period import LotAuctionPeriod

# -- START model for view ---


class PostLot(PostBaseLot, LotGuaranteeSerializerMixin):
    guarantee = ModelType(Guarantee)


class PatchLot(BaseLot):
    title = StringType()
    guarantee = ModelType(Guarantee)
    minimalStep = ModelType(Value)
    status = StringType(choices=["active"])


# -- END models for view ---


class PostTenderLot(PostLot, TenderLotMixin):
    pass


class PatchTenderLot(BaseLot, TenderLotMixin):
    title = StringType()
    guarantee = ModelType(Guarantee)
    minimalStep = ModelType(Value)


class Lot(BaseLot, TenderLotMixin, LotGuaranteeSerializerMixin):
    id = MD5Type(required=True)
    value = ModelType(Value)
    minimalStep = ModelType(Value)
    guarantee = ModelType(Guarantee)

    auctionPeriod = ModelType(LotAuctionPeriod)
    auctionUrl = URLType()
    numberOfBids = BaseType()  # deprecated

    def validate_minimalStep(self, data, value):
        if value and value.amount and data.get("value") and data.get("value").amount < value.amount:
            raise ValidationError("value should be less than value of lot")
