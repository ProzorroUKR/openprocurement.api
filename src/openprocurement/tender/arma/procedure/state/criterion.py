from openprocurement.tender.arma.procedure.state.tender import ARMATenderState
from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin


class ARMACriterionState(CriterionStateMixin, ARMATenderState):
    pass
