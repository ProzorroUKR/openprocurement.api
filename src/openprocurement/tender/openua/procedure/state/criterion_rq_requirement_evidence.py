from openprocurement.tender.core.procedure.state.criterion_rq_requirement_evidence import EligibleEvidenceStateMixin
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


class OpenUAEligibleEvidenceState(EligibleEvidenceStateMixin, OpenUATenderState):
    pass
