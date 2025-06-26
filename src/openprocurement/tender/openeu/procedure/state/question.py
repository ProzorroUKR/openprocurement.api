from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState
from openprocurement.tender.openua.procedure.state.question import (
    UATenderQuestionStateMixin,
)


class EUTenderQuestionState(UATenderQuestionStateMixin, BaseOpenEUTenderState):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)
