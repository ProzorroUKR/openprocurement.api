from openprocurement.tender.core.procedure.state.criterion_rq_requirement_evidence import (
    EligibleEvidenceStateMixin,
)

# from openprocurement.tender.pricequotation.procedure.state.criterion import PQCriterionStateMixin
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PriceQuotationTenderState,
)

# class PQEligibleEvidenceStateMixin(PQCriterionStateMixin, EligibleEvidenceStateMixin):
#     pass


class PQEligibleEvidenceState(EligibleEvidenceStateMixin, PriceQuotationTenderState):
    tender_valid_statuses = ["draft"]
    evidence_status_check_always = True
