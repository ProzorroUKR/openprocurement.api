from openprocurement.tender.cfaselectionua.procedure.state.tender import (
    CFASelectionTenderState,
)
from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin


class CFASelectionCriterionState(CriterionStateMixin, CFASelectionTenderState):
    criterion_patch_exclusion_check = False
    criterion_allowed_tender_statuses = ["draft", "active.enquiries"]
