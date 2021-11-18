from openprocurement.tender.openua.procedure.models.award import (
    Award as BaseUAAward,
    PostAward as BaseUAPostAward,
    PatchAward as BaseUAPatchAward,
)
from openprocurement.tender.openeu.procedure.models.award import (
    Award as BaseEUAward,
    PostAward as BaseEUPostAward,
    PatchAward as BaseEUPatchAward,
)
from openprocurement.tender.core.procedure.models.base import ModelType, ListType
from openprocurement.tender.competitivedialogue.procedure.models.item import Item


class UAAward(BaseUAAward):
    items = ListType(ModelType(Item))


class UAPostAward(BaseUAPostAward):
    items = ListType(ModelType(Item))


class UAPatchAward(BaseUAPatchAward):
    items = ListType(ModelType(Item))


class EUAward(BaseEUAward):
    items = ListType(ModelType(Item))


class EUPostAward(BaseEUPostAward):
    items = ListType(ModelType(Item))


class EUPatchAward(BaseEUPatchAward):
    items = ListType(ModelType(Item))
