from openprocurement.api.auth import ACCR_4
from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.openua.procedure.state.question import UATenderQuestionStateMixin


class CFAUATenderQuestionState(UATenderQuestionStateMixin, CFAUATenderState):
    create_accreditations = (ACCR_4,)
