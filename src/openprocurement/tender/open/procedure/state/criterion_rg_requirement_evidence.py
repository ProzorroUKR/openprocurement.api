from openprocurement.tender.core.procedure.state.criterion_rq_requirement_evidence import (
    EligibleEvidenceStateMixin,
)
from openprocurement.tender.open.procedure.state.criterion_rg_requirement import (
    BelowThresholdRequirementValidationsMixin,
    RFPRequirementValidationsMixin,
)
from openprocurement.tender.open.procedure.state.tender import (
    AboveThresholdEUTenderState,
    BelowThresholdTenderState,
    RFPTenderState,
)


class AboveThresholdEUEligibleEvidenceState(EligibleEvidenceStateMixin, AboveThresholdEUTenderState):
    pass


class BelowThresholdEligibleEvidenceStateMixin(BelowThresholdRequirementValidationsMixin, EligibleEvidenceStateMixin):
    pass


class BelowThresholdEligibleEvidenceState(BelowThresholdEligibleEvidenceStateMixin, BelowThresholdTenderState):
    pass


class RFPEligibleEvidenceStateMixin(RFPRequirementValidationsMixin, EligibleEvidenceStateMixin):
    pass


class RFPEligibleEvidenceState(RFPEligibleEvidenceStateMixin, RFPTenderState):
    pass
