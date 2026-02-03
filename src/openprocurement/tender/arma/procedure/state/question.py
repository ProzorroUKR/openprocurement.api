from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.openua.procedure.state.question import (
    UATenderQuestionStateMixin,
)


class QuestionState(UATenderQuestionStateMixin, TenderState):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)
