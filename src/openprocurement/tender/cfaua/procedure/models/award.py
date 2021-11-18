from openprocurement.tender.core.procedure.models.award import (
    Award as BaseAward,
    PatchAward as BasePatchAward,
    PostAward as BasePostAward,
)
from openprocurement.tender.core.procedure.models.milestone import QualificationMilestoneListMixin
from schematics.types import BooleanType


class Award(QualificationMilestoneListMixin, BaseAward):
    eligible = BooleanType()


class PatchAward(BasePatchAward):
    eligible = BooleanType()


class PostAward(BasePostAward):
    pass
