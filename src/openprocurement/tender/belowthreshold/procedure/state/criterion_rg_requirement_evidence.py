from openprocurement.tender.core.procedure.state.criterion_rq_requirement_evidence import EligibleEvidenceStateMixin
from openprocurement.tender.belowthreshold.procedure.state.criterion_rg_requirement import (
    BelowThresholdRequirementValidationsMixin,
)
from openprocurement.tender.belowthreshold.procedure.state.tender import BelowThresholdTenderState


class BelowThresholdEligibleEvidenceStateMixin(
    BelowThresholdRequirementValidationsMixin,
    EligibleEvidenceStateMixin
):
    pass


class BelowThresholdEligibleEvidenceState(
    BelowThresholdEligibleEvidenceStateMixin,
    BelowThresholdTenderState
):
    pass
