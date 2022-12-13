from openprocurement.tender.core.procedure.state.criterion_rq_requirement_evidence import EligibleEvidenceStateMixin
from openprocurement.tender.openeu.procedure.state.tender import OpenEUTenderState


class OpenEUEligibleEvidenceState(EligibleEvidenceStateMixin, OpenEUTenderState):
    pass
