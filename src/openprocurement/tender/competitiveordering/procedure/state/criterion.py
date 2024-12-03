from openprocurement.tender.competitiveordering.procedure.state.tender import (
    OpenTenderState,
)
from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin


class OpenCriterionState(CriterionStateMixin, OpenTenderState):
    pass
