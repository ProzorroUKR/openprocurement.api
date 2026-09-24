from openprocurement.tender.cfaselectionua.procedure.state.tender import (
    CFASelectionTenderState,
)
from openprocurement.tender.core.procedure.state.criterion_rg import RequirementGroupStateMixin


class CFASelectionRequirementGroupState(RequirementGroupStateMixin, CFASelectionTenderState):
    tender_valid_statuses = ["draft", "active.enquiries"]
