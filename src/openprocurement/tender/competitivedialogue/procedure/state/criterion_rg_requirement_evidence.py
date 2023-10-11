from openprocurement.tender.core.procedure.state.criterion_rq_requirement_evidence import EligibleEvidenceStateMixin
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import CDStage1TenderState


class CDEligibleEvidenceState(EligibleEvidenceStateMixin, CDStage1TenderState):
    pass
