from openprocurement.tender.belowthreshold.procedure.state.criterion import (
    BelowThresholdCriterionStatusesMixin,
)
from openprocurement.tender.belowthreshold.procedure.state.tender import (
    BelowThresholdTenderState,
)
from openprocurement.tender.core.procedure.state.criterion_rg_requirement import (
    RequirementStateMixin,
)


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
