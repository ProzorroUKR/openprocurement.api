from openprocurement.tender.cfaua.procedure.state.tender_details import (
    CFAUATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin


class CFAUACriterionState(CriterionStateMixin, CFAUATenderDetailsState):
    pass
