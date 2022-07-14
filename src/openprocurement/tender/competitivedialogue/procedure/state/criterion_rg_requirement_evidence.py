from openprocurement.tender.core.procedure.state.criterion_rq_requirement_evidence import EligibleEvidenceStateMixin
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import Stage1TenderState


class Stage1EligibleEvidenceState(EligibleEvidenceStateMixin, Stage1TenderState):
    pass
