from openprocurement.tender.cfaselectionua.procedure.state.tender_details import (
    CFASelectionTenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin


class CFASelectionCriterionState(CriterionStateMixin, CFASelectionTenderDetailsState):
    pass
