from openprocurement.tender.cfaua.procedure.state.tender_details import (
    CFAUATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion_rg_requirement_evidence import EligibleEvidenceStateMixin


class CFAUAEligibleEvidenceState(EligibleEvidenceStateMixin, CFAUATenderDetailsState):
    pass
