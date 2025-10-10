from schematics.exceptions import ValidationError
from schematics.types import BooleanType

from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.tender.core.procedure.models.award import Award as BaseAward
from openprocurement.tender.core.procedure.models.award import (
    PatchAward as BasePatchAward,
)
from openprocurement.tender.core.procedure.models.award import (
    PostAward as BasePostAward,
)
from openprocurement.tender.esco.procedure.models.item import Item
from openprocurement.tender.esco.procedure.models.value import (
    ESCOValue,
    ESCOWeightedValue,
)


class Award(BaseAward):
    value = ModelType(ESCOValue)
    weightedValue = ModelType(ESCOWeightedValue)
    eligible = BooleanType()
    items = ListType(ModelType(Item, required=True))

    def validate_eligible(self, data, eligible):
        if data["status"] == "active" and not eligible:
            raise ValidationError("Can't update award to active status with not eligible")


class PatchAward(BasePatchAward):
    eligible = BooleanType()
    items = ListType(ModelType(Item, required=True))


class PostAward(BasePostAward):
    value = ModelType(ESCOValue)
    weightedValue = ModelType(ESCOWeightedValue)
    items = ListType(ModelType(Item, required=True))
