from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.tender.competitivedialogue.procedure.models.item import Item
from openprocurement.tender.openeu.procedure.models.award import Award as BaseEUAward
from openprocurement.tender.openeu.procedure.models.award import (
    PatchAward as BaseEUPatchAward,
)
from openprocurement.tender.openeu.procedure.models.award import (
    PostAward as BaseEUPostAward,
)
from openprocurement.tender.openua.procedure.models.award import Award as BaseUAAward
from openprocurement.tender.openua.procedure.models.award import (
    PatchAward as BaseUAPatchAward,
)
from openprocurement.tender.openua.procedure.models.award import (
    PostAward as BaseUAPostAward,
)


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
