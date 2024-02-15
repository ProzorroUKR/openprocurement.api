from schematics.types import BooleanType

from openprocurement.tender.core.procedure.models.award import Award as BaseAward
from openprocurement.tender.core.procedure.models.award import (
    PatchAward as BasePatchAward,
)
from openprocurement.tender.core.procedure.models.award import (
    PostAward as BasePostAward,
)
from openprocurement.tender.core.procedure.models.milestone import (
    QualificationMilestoneListMixin,
)


class Award(QualificationMilestoneListMixin, BaseAward):
    eligible = BooleanType()


class PatchAward(BasePatchAward):
    eligible = BooleanType()


class PostAward(BasePostAward):
    pass
