from openprocurement.tender.cfaselectionua.procedure.state.tender_details import (
    CFASelectionTenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion_rg_requirement import RequirementStateMixin


class CFASelectionRequirementState(RequirementStateMixin, CFASelectionTenderDetailsState):
    pass
