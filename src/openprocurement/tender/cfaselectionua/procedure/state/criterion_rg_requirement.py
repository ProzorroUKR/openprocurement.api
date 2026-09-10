from openprocurement.tender.belowthreshold.procedure.state.criterion_rg_requirement import (
    BelowThresholdRequirementStateMixin,
)
from openprocurement.tender.cfaselectionua.procedure.state.tender import (
    CFASelectionTenderState,
)


class CFASelectionRequirementState(BelowThresholdRequirementStateMixin, CFASelectionTenderState):
    allowed_put_statuses = ["active.enquiries", "active.tendering"]
    requirement_post_ids_uniq_check = False
