from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class OpenCriterionState(CriterionStateMixin, OpenTenderState):
    pass
