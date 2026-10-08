from openprocurement.tender.arma.procedure.state.tender import ARMATenderState
from openprocurement.tender.core.procedure.state.question import TenderQuestionStateMixin


class ARMAQuestionState(TenderQuestionStateMixin, ARMATenderState):
    pass
