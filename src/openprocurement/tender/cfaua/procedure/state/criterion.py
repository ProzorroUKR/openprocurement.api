from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin
from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState


class CFAUACriterionState(CriterionStateMixin, CFAUATenderState):
    pass
