from openprocurement.tender.cfaselectionua.procedure.state.tender import (
    CFASelectionTenderState,
)
from openprocurement.tender.core.procedure.state.criterion_rq_requirement_evidence import EligibleEvidenceStateMixin


class CFASelectionEligibleEvidenceState(EligibleEvidenceStateMixin, CFASelectionTenderState):
    requirement_models_by_classification = False
    requirement_change_valid_statuses = ("draft",)
    requirement_change_legacy_status = "active.enquiries"
