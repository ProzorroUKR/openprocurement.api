from openprocurement.tender.cfaselectionua.procedure.state.tender_details import (
    CFASelectionTenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion_rg import RequirementGroupStateMixin


class CFASelectionRequirementGroupState(RequirementGroupStateMixin, CFASelectionTenderDetailsState):
    pass
