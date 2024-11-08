from openprocurement.tender.core.procedure.state.criterion_rq_requirement_evidence import (
    EligibleEvidenceStateMixin,
)
from openprocurement.tender.requestforproposal.procedure.state.criterion_rg_requirement import (
    RequestForProposalRequirementValidationsMixin,
)
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RequestForProposalTenderState,
)


class RequestForProposalEligibleEvidenceStateMixin(
    RequestForProposalRequirementValidationsMixin, EligibleEvidenceStateMixin
):
    pass


class RequestForProposalEligibleEvidenceState(
    RequestForProposalEligibleEvidenceStateMixin, RequestForProposalTenderState
):
    pass
