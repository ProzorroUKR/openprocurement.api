from openprocurement.tender.cfaua.procedure.state.tender_details import (
    CFAUATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion_rg import RequirementGroupStateMixin


class CFAUARequirementGroupState(RequirementGroupStateMixin, CFAUATenderDetailsState):
    pass
