from openprocurement.tender.core.procedure.state.criterion_rg import (
    RequirementGroupStateMixin,
)
from openprocurement.tender.open.procedure.state.criterion import (
    BelowThresholdCriterionStatusesMixin,
    RFPCriterionStatusesMixin,
)
from openprocurement.tender.open.procedure.state.tender import (
    AboveThresholdEUTenderState,
    AboveThresholdTenderState,
    AboveThresholdUATenderState,
    BelowThresholdTenderState,
    COTenderState,
    RFPTenderState,
)


class AboveThresholdRequirementGroupState(RequirementGroupStateMixin, AboveThresholdTenderState):
    pass


class AboveThresholdUARequirementGroupState(RequirementGroupStateMixin, AboveThresholdUATenderState):
    pass


class AboveThresholdEURequirementGroupState(RequirementGroupStateMixin, AboveThresholdEUTenderState):
    pass


class CORequirementGroupState(RequirementGroupStateMixin, COTenderState):
    pass


class BelowThresholdRequirementGroupStateMixin(
    BelowThresholdCriterionStatusesMixin,
    RequirementGroupStateMixin,
):
    pass


class BelowThresholdRequirementGroupState(
    BelowThresholdRequirementGroupStateMixin,
    BelowThresholdTenderState,
):
    pass


class RFPRequirementGroupStateMixin(
    RFPCriterionStatusesMixin,
    RequirementGroupStateMixin,
):
    pass


class RFPRequirementGroupState(
    RFPRequirementGroupStateMixin,
    RFPTenderState,
):
    pass
