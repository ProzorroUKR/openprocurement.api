from schematics.types import BooleanType, BaseType
from schematics.types.compound import ModelType
from openprocurement.api.models import ListType
from openprocurement.tender.core.procedure.models.award import (
    Award as BaseAward,
    PatchAward as BasePatchAward,
    PostAward as BasePostAward,
)
from openprocurement.tender.core.procedure.models.milestone import QualificationMilestoneListMixin
from openprocurement.tender.core.procedure.models.guarantee import WeightedValue
from openprocurement.tender.openua.procedure.models.item import Item


class Award(QualificationMilestoneListMixin, BaseAward):
    complaints = BaseType()
    items = ListType(ModelType(Item, required=True))
    qualified = BooleanType()
    eligible = BooleanType()
    weightedValue = ModelType(WeightedValue)


class PatchAward(BasePatchAward):
    items = ListType(ModelType(Item, required=True))
    qualified = BooleanType()
    eligible = BooleanType()


class PostAward(BasePostAward):
    weightedValue = ModelType(WeightedValue)
