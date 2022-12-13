from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


class OpenUACriterionState(CriterionStateMixin, OpenUATenderState):
    pass
