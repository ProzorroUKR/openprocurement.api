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

    def evidence_always(self, data: dict) -> None:
        self._validate_operation_criterion_in_tender_status()
        super().evidence_always(data)
