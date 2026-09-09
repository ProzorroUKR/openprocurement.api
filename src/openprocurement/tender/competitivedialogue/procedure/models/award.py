from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.tender.competitivedialogue.procedure.models.item import CDItem
from openprocurement.tender.core.procedure.models.award import Award, PatchAward, PostAward


class CDAward(Award):
    items = ListType(ModelType(CDItem))


class CDPostAward(PostAward):
    items = ListType(ModelType(CDItem))


class CDPatchAward(PatchAward):
    items = ListType(ModelType(CDItem))
