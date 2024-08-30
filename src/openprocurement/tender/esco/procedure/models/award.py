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
from openprocurement.tender.esco.procedure.models.value import BaseESCOValue


class Award(BaseAward):
    value = ModelType(BaseESCOValue)
    weightedValue = ModelType(BaseESCOValue)
    items = ListType(ModelType(Item, required=True))


class PatchAward(BasePatchAward):
    items = ListType(ModelType(Item, required=True))


class PostAward(BasePostAward):
    value = ModelType(BaseESCOValue)
    weightedValue = ModelType(BaseESCOValue)
    items = ListType(ModelType(Item, required=True))
