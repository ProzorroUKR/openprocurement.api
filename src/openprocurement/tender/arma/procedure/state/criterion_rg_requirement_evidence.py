from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.criterion_rq_requirement_evidence import (
    EligibleEvidenceStateMixin,
)


class EligibleEvidenceState(EligibleEvidenceStateMixin, TenderState):
    pass
