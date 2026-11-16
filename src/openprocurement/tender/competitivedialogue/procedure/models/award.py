from openprocurement.tender.competitivedialogue.procedure.models.item import CDItem
from openprocurement.tender.core.procedure.models.award import Award, PatchAward, PostAward


class CDAward(Award):
    items: list[CDItem] | None = None


class CDPostAward(PostAward):
    items: list[CDItem] | None = None


class CDPatchAward(PatchAward):
    items: list[CDItem] | None = None
