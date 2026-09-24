from openprocurement.tender.belowthreshold.procedure.state.criterion import (
    BaseBelowThresholdCriterionStateMixin,
)
from openprocurement.tender.belowthreshold.procedure.state.tender import (
    BelowThresholdTenderState,
)
from openprocurement.tender.core.procedure.state.criterion_rg_requirement import (
    RequirementStateMixin,
)


class BelowThresholdRequirementValidationsMixin:
    requirement_models_by_classification = False
    requirement_change_valid_statuses = ("draft",)
    requirement_change_legacy_status = "active.enquiries"


class BelowThresholdRequirementStateMixin(
    BelowThresholdRequirementValidationsMixin,
    BaseBelowThresholdCriterionStateMixin,
    RequirementStateMixin,
):
    pass


class BelowThresholdRequirementState(BelowThresholdRequirementStateMixin, BelowThresholdTenderState):
    allowed_put_statuses = ["active.enquiries"]
