from schematics.types.compound import ModelType
from schematics.types import URLType, StringType, MD5Type, BaseType
from schematics.types.serializable import serializable
from schematics.validate import ValidationError

from openprocurement.tender.core.procedure.models.guarantee import Guarantee, Value
from openprocurement.tender.core.procedure.models.period import LotAuctionPeriod
from openprocurement.tender.core.procedure.models.lot import (
    PostBaseLot,
    PatchBaseLot,
    TenderLotMixin,
    LotGuaranteeSerializerMixin,
    BaseLot,
)


# -- START model for view ---

class PostLot(PostBaseLot, LotGuaranteeSerializerMixin):
    guarantee = ModelType(Guarantee)


class PatchLot(PatchBaseLot):
    title = StringType()
    guarantee = ModelType(Guarantee)
    minimalStep = ModelType(Value)

# -- END models for view ---


class PostTenderLot(PostLot, TenderLotMixin):
    pass


class PatchTenderLot(PatchBaseLot, TenderLotMixin):
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
        if (
            value
            and value.amount
            and data.get("value")
            and data.get("value").amount < value.amount
        ):
            raise ValidationError("value should be less than value of lot")
