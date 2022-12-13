from openprocurement.tender.core.procedure.state.criterion_rq_requirement_evidence import EligibleEvidenceStateMixin
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class OpenEligibleEvidenceState(EligibleEvidenceStateMixin, OpenTenderState):
    pass
