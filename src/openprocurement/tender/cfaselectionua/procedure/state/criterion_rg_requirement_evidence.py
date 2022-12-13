from openprocurement.tender.belowthreshold.procedure.state.criterion_rg_requirement_evidence import (
    BelowThresholdEligibleEvidenceStateMixin,
)
from openprocurement.tender.cfaselectionua.procedure.state.tender import CFASelectionTenderState


class CFASelectionEligibleEvidenceState(
    BelowThresholdEligibleEvidenceStateMixin,
    CFASelectionTenderState
):
    pass
