from openprocurement.tender.core.procedure.state.criterion_rq_requirement_evidence import (
    EligibleEvidenceStateMixin,
)
from openprocurement.tender.requestforproposal.procedure.state.criterion_rg_requirement import (
    RFPRequirementValidationsMixin,
)
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RFPTenderState,
)


class RFPEligibleEvidenceStateMixin(RFPRequirementValidationsMixin, EligibleEvidenceStateMixin):
    pass


class RFPEligibleEvidenceState(RFPEligibleEvidenceStateMixin, RFPTenderState):
    pass
