from openprocurement.tender.arma.procedure.state.tender import ARMATenderState
from openprocurement.tender.core.procedure.state.criterion_rq_requirement_evidence import (
    EligibleEvidenceStateMixin,
)


class ARMAEligibleEvidenceState(EligibleEvidenceStateMixin, ARMATenderState):
    pass
