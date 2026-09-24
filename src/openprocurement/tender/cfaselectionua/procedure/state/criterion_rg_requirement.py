from openprocurement.tender.cfaselectionua.procedure.state.tender import (
    CFASelectionTenderState,
)
from openprocurement.tender.core.procedure.state.criterion_rg_requirement import RequirementStateMixin


class CFASelectionRequirementState(RequirementStateMixin, CFASelectionTenderState):
    requirement_models_by_classification = False
    requirement_change_valid_statuses = ("draft",)
    requirement_change_legacy_status = "active.enquiries"
    tender_valid_statuses = ["draft", "active.enquiries"]
    allowed_put_statuses = ["active.enquiries", "active.tendering"]
    requirement_post_ids_uniq_check = False
