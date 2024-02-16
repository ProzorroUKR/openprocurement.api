from openprocurement.tender.core.procedure.state.criterion_rq_requirement_evidence import (
    EligibleEvidenceStateMixin,
)
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState


class ESCOEligibleEvidenceState(EligibleEvidenceStateMixin, ESCOTenderState):
    pass
