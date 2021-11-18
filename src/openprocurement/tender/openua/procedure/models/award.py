from schematics.types import StringType, BooleanType, MD5Type, BaseType
from schematics.exceptions import ValidationError
from schematics.types.compound import ModelType
from openprocurement.api.models import ListType
from openprocurement.tender.core.procedure.models.award import (
    Award as BaseAward,
    PatchAward as BasePatchAward,
    PostAward as BasePostAward,
)
from openprocurement.tender.core.procedure.models.milestone import QualificationMilestoneListMixin
from openprocurement.tender.openua.procedure.models.item import Item


class Award(QualificationMilestoneListMixin, BaseAward):
    complaints = BaseType()
    items = ListType(ModelType(Item, required=True))
    qualified = BooleanType(default=False)
    eligible = BooleanType(default=False)

    def validate_qualified(self, data, qualified):
        if data["status"] == "active" and not qualified:
            raise ValidationError("This field is required.")

    def validate_eligible(self, data, eligible):
        if data["status"] == "active" and not eligible:
            raise ValidationError("This field is required.")


class PatchAward(BasePatchAward):
    items = ListType(ModelType(Item, required=True))
    qualified = BooleanType()
    eligible = BooleanType()


class PostAward(BasePostAward):
    pass
