from openprocurement.tender.competitiveordering.procedure.state.tender import (
    COTenderState,
)
from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin


class COCriterionState(CriterionStateMixin, COTenderState):
    pass
