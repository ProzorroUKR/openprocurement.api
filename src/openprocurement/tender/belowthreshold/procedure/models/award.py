from openprocurement.tender.core.procedure.models.award import Award as BaseAward
from openprocurement.tender.core.procedure.models.award import (
    PatchAward as BasePatchAward,
)
from openprocurement.tender.core.procedure.models.milestone import (
    QualificationMilestoneListMixin,
)


class Award(QualificationMilestoneListMixin, BaseAward):
    pass


class PatchAward(BasePatchAward):
    pass
