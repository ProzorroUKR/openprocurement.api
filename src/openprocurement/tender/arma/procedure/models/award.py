from openprocurement.api.procedure.models.value import AmountPercentageValue
from openprocurement.api.procedure.types import ModelType
from openprocurement.tender.arma.procedure.models.award_milestone import ARMAAwardMilestoneListMixin
from openprocurement.tender.core.procedure.models.award import Award, PostAward
from openprocurement.tender.core.procedure.models.value import AmountPercentageWeightedValue


class ARMAAward(ARMAAwardMilestoneListMixin, Award):
    weightedValue = ModelType(AmountPercentageWeightedValue)
    value = ModelType(AmountPercentageValue)


class ARMAPostAward(PostAward):
    weightedValue = ModelType(AmountPercentageWeightedValue)
    value = ModelType(AmountPercentageValue)
