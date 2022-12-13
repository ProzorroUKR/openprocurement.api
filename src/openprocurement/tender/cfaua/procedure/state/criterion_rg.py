from openprocurement.tender.core.procedure.state.criterion_rg import RequirementGroupStateMixin
from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState


class CFAUARequirementGroupState(RequirementGroupStateMixin, CFAUATenderState):
    pass
