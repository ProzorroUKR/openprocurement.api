from openprocurement.tender.competitiveordering.procedure.state.tender import (
    OpenTenderState,
)
from openprocurement.tender.core.procedure.state.criterion_rq_requirement_evidence import (
    EligibleEvidenceStateMixin,
)


class OpenEligibleEvidenceState(EligibleEvidenceStateMixin, OpenTenderState):
    pass
