from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.core.procedure.state.criterion_rq_requirement_evidence import (
    EligibleEvidenceStateMixin,
)


class CFAUAEligibleEvidenceState(EligibleEvidenceStateMixin, CFAUATenderState):
    pass
