from schematics.types import BooleanType

from openprocurement.tender.core.procedure.models.award import Award as BaseAward
from openprocurement.tender.core.procedure.models.award import (
    PatchAward as BasePatchAward,
)
from openprocurement.tender.core.procedure.models.award import (
    PostAward as BasePostAward,
)


class Award(BaseAward):
    eligible = BooleanType()


class PatchAward(BasePatchAward):
    eligible = BooleanType()


class PostAward(BasePostAward):
    pass
