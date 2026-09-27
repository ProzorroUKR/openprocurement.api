from openprocurement.tender.cfaua.procedure.state.tender_details import (
    CFAUATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion_rg_requirement import RequirementStateMixin


class CFAUARequirementState(RequirementStateMixin, CFAUATenderDetailsState):
    pass
