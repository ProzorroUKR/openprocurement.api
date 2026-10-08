from openprocurement.tender.core.procedure.state.criterion_rg_requirement_evidence import EligibleEvidenceStateMixin
from openprocurement.tender.pricequotation.procedure.state.tender_details import (
    PQTenderDetailsState,
)


class PQEligibleEvidenceState(EligibleEvidenceStateMixin, PQTenderDetailsState):
    pass
