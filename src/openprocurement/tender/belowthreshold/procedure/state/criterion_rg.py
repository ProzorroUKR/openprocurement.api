from openprocurement.tender.belowthreshold.procedure.state.criterion import BaseBelowThresholdCriterionStateMixin
from openprocurement.tender.belowthreshold.procedure.state.tender import BelowThresholdTenderState
from openprocurement.tender.core.procedure.state.criterion_rg import RequirementGroupStateMixin


class BelowThresholdRequirementGroupStateMixin(
    BaseBelowThresholdCriterionStateMixin,
    RequirementGroupStateMixin,
):
    pass


class BelowThresholdRequirementGroupState(
    BelowThresholdRequirementGroupStateMixin,
    BelowThresholdTenderState,
):
    pass
