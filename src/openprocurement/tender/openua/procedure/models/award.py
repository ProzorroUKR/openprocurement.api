from schematics.exceptions import ValidationError
from schematics.types import BaseType, BooleanType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.types import ListType
from openprocurement.tender.core.procedure.models.award import Award as BaseAward
from openprocurement.tender.core.procedure.models.award import (
    PatchAward as BasePatchAward,
)
from openprocurement.tender.core.procedure.models.award import (
    PostAward as BasePostAward,
)
from openprocurement.tender.openua.procedure.models.item import Item


class Award(BaseAward):
    complaints = BaseType()
    items = ListType(ModelType(Item, required=True))
    eligible = BooleanType()

    def validate_eligible(self, data, eligible):
        if data["status"] == "active" and not eligible:
            raise ValidationError("Can't update award to active status with not eligible")


class PatchAward(BasePatchAward):
    items = ListType(ModelType(Item, required=True))
    eligible = BooleanType()


class PostAward(BasePostAward):
    pass
