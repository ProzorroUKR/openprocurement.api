from schematics.types.compound import ModelType
from schematics.types import StringType
from schematics.types.serializable import serializable
from openprocurement.api.models import MD5Type
from openprocurement.tender.core.procedure.models.guarantee import Value, PostValue
from openprocurement.tender.core.procedure.models.lot import (
    BaseLot,
    PostBaseLot,
    PatchBaseLot,
    TenderLotMixin,
    BaseLotSerializersMixin,
)


class LotValueSerializerMixin(BaseLotSerializersMixin):
    @serializable(serialized_name="value", type=ModelType(Value))
    def lot_value(self):
        tender = self.get_tender()
        return Value(
            dict(
                amount=self.value.amount,
                currency=tender["value"]["currency"],
                valueAddedTaxIncluded=tender["value"]["valueAddedTaxIncluded"],
            )
        )


class PostLot(PostBaseLot, LotValueSerializerMixin):
    value = ModelType(PostValue, required=True)


class PatchLot(PatchBaseLot):
    title = StringType()
    value = ModelType(Value)


class PostTenderLot(PostLot, TenderLotMixin):
    pass


class PatchTenderLot(PatchBaseLot, TenderLotMixin):
    value = ModelType(Value, required=True)


class Lot(BaseLot, TenderLotMixin, LotValueSerializerMixin):
    value = ModelType(Value, required=True)

