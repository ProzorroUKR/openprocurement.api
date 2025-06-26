from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.openua.procedure.state.question import (
    UATenderQuestionStateMixin,
)


class CFAUATenderQuestionState(UATenderQuestionStateMixin, CFAUATenderState):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)
