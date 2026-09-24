from openprocurement.tender.core.procedure.state.criterion_rg_requirement import (
    RequirementStateMixin,
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


class AboveThresholdRequirementState(RequirementStateMixin, AboveThresholdTenderState):
    pass


class AboveThresholdUARequirementState(RequirementStateMixin, AboveThresholdUATenderState):
    pass


class AboveThresholdEURequirementState(RequirementStateMixin, AboveThresholdEUTenderState):
    pass


class CORequirementState(RequirementStateMixin, COTenderState):
    pass


class BelowThresholdRequirementValidationsMixin:
    requirement_models_by_classification = False
    requirement_change_allowed_tender_statuses = ("draft",)
    requirement_change_legacy_status = "active.enquiries"


class BelowThresholdRequirementStateMixin(
    BelowThresholdRequirementValidationsMixin,
    BelowThresholdCriterionStatusesMixin,
    RequirementStateMixin,
):
    pass


class BelowThresholdRequirementState(BelowThresholdRequirementStateMixin, BelowThresholdTenderState):
    requirement_put_allowed_tender_statuses = ["active.enquiries"]


class RFPRequirementValidationsMixin:
    requirement_models_by_classification = False
    requirement_change_allowed_tender_statuses = ("draft",)
    requirement_change_legacy_status = "active.enquiries"


class RFPRequirementStateMixin(
    RFPRequirementValidationsMixin,
    RFPCriterionStatusesMixin,
    RequirementStateMixin,
):
    pass


class RFPRequirementState(RFPRequirementStateMixin, RFPTenderState):
    requirement_put_allowed_tender_statuses = ["active.enquiries"]
