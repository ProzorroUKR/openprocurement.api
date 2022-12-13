from openprocurement.tender.core.procedure.state.criterion_rq_requirement_evidence import EligibleEvidenceStateMixin
from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState


class CFAUAEligibleEvidenceState(EligibleEvidenceStateMixin, CFAUATenderState):
    pass
