from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin


class CriterionState(CriterionStateMixin, TenderState):
    pass
