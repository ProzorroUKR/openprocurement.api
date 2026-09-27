from openprocurement.tender.cfaselectionua.procedure.state.tender_details import (
    CFASelectionTenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion_rg_requirement_evidence import EligibleEvidenceStateMixin


class CFASelectionEligibleEvidenceState(EligibleEvidenceStateMixin, CFASelectionTenderDetailsState):
    pass
