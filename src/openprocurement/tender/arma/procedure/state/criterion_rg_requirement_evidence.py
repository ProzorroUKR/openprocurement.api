from openprocurement.tender.arma.procedure.state.tender_details import (
    ARMATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion_rg_requirement_evidence import EligibleEvidenceStateMixin


class ARMAEligibleEvidenceState(EligibleEvidenceStateMixin, ARMATenderDetailsState):
    pass
