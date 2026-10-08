from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.core.procedure.state.question import TenderQuestionStateMixin


class CFAUATenderQuestionState(TenderQuestionStateMixin, CFAUATenderState):
    pass
