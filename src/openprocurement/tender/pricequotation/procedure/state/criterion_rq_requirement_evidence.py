from openprocurement.tender.core.procedure.state.criterion_rq_requirement_evidence import (
    EligibleEvidenceStateMixin,
)

# from openprocurement.tender.pricequotation.procedure.state.criterion import PQCriterionStateMixin
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PQTenderState,
)

# class PQEligibleEvidenceStateMixin(PQCriterionStateMixin, EligibleEvidenceStateMixin):
#     pass


class PQEligibleEvidenceState(EligibleEvidenceStateMixin, PQTenderState):
    criterion_allowed_tender_statuses = ["draft"]
    evidence_status_check_always = True
