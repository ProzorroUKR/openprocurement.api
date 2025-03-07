from schematics.exceptions import ValidationError
from schematics.types import BaseType, BooleanType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.types import ListType
from openprocurement.tender.competitiveordering.procedure.models.item import Item
from openprocurement.tender.core.procedure.models.award import Award as BaseAward
from openprocurement.tender.core.procedure.models.award import (
    PatchAward as BasePatchAward,
)
from openprocurement.tender.core.procedure.models.award import (
    PostAward as BasePostAward,
)


class Award(BaseAward):
    complaints = BaseType()
    items = ListType(ModelType(Item, required=True))
    eligible = BooleanType()

    def validate_qualified(self, data, qualified):
        if data["status"] == "active" and not qualified:
            raise ValidationError("Can't update award to active status with not qualified")


class PatchAward(BasePatchAward):
    items = ListType(ModelType(Item, required=True))
    eligible = BooleanType()


class PostAward(BasePostAward):
    pass
