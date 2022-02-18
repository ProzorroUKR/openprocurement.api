from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from openprocurement.api.models import Value
from openprocurement.tender.core.procedure.models.lot import BaseLot, PostBaseLot, PatchBaseLot


class PostLot(PostBaseLot):
    value = ModelType(Value, required=True)
    #
    # @serializable(serialized_name="value", type=ModelType(Value))
    # def lot_value(self):
    #     return Value(
    #         dict(
    #             amount=self.value.amount,
    #             currency=self.__parent__.value.currency,
    #             valueAddedTaxIncluded=self.__parent__.value.valueAddedTaxIncluded,
    #         )
    #     )


class PatchLot(PatchBaseLot):
    value = ModelType(Value, required=True)


class Lot(BaseLot):
    value = ModelType(Value, required=True)

