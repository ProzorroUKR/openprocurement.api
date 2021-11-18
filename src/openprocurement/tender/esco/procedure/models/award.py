from openprocurement.tender.core.procedure.models.base import ModelType
from openprocurement.tender.core.procedure.models.award import (
    Award as BaseAward,
    PatchAward as BasePatchAward,
    PostAward as BasePostAward,
)
from openprocurement.tender.esco.procedure.models.value import BaseESCOValue
from schematics.types import BooleanType


class Award(BaseAward):
    value = ModelType(BaseESCOValue)
    eligible = BooleanType()


class PatchAward(BasePatchAward):
    eligible = BooleanType()


class PostAward(BasePostAward):
    value = ModelType(BaseESCOValue)
