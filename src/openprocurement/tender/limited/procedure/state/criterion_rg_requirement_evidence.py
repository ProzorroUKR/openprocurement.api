from openprocurement.tender.core.procedure.state.criterion_rq_requirement_evidence import (
    EligibleEvidenceStateMixin,
)
from openprocurement.tender.core.procedure.state.tender import TenderState


class LimitedEligibleEvidenceState(EligibleEvidenceStateMixin, TenderState):
    pass
