from openprocurement.tender.cfaselectionua.procedure.state.tender import (
    CFASelectionTenderState,
)
from openprocurement.tender.core.procedure.state.criterion_rg_requirement import (
    RequirementStateMixin,
)


class CFAUARequirementState(RequirementStateMixin, CFASelectionTenderState):
    pass
