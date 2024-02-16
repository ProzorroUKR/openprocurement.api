from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.core.procedure.state.criterion_rg import (
    RequirementGroupStateMixin,
)


class CFAUARequirementGroupState(RequirementGroupStateMixin, CFAUATenderState):
    pass
