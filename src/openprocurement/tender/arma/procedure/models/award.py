from openprocurement.api.procedure.models.value import AmountPercentageValue
from openprocurement.tender.arma.procedure.models.award_milestone import ARMAAwardMilestoneListMixin
from openprocurement.tender.core.procedure.models.award import Award, PostAward
from openprocurement.tender.core.procedure.models.value import AmountPercentageWeightedValue


class ARMAAward(ARMAAwardMilestoneListMixin, Award):
    weightedValue: AmountPercentageWeightedValue | None = None
    value: AmountPercentageValue | None = None


class ARMAPostAward(PostAward):
    weightedValue: AmountPercentageWeightedValue | None = None
    value: AmountPercentageValue | None = None
