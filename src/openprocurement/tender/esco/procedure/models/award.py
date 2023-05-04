from openprocurement.tender.core.procedure.models.base import ModelType, ListType
from openprocurement.tender.core.procedure.models.award import (
    Award as BaseAward,
    PatchAward as BasePatchAward,
    PostAward as BasePostAward,
)
from openprocurement.tender.esco.procedure.models.value import BaseESCOValue
from openprocurement.tender.esco.procedure.models.item import Item
from schematics.types import BooleanType


class Award(BaseAward):
    value = ModelType(BaseESCOValue)
    weightedValue = ModelType(BaseESCOValue)
    eligible = BooleanType()
    items = ListType(ModelType(Item, required=True))


class PatchAward(BasePatchAward):
    eligible = BooleanType()
    items = ListType(ModelType(Item, required=True))


class PostAward(BasePostAward):
    value = ModelType(BaseESCOValue)
    weightedValue = ModelType(BaseESCOValue)
    items = ListType(ModelType(Item, required=True))
