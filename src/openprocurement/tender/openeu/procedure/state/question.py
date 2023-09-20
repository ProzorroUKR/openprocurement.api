from openprocurement.api.auth import ACCR_4
from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState
from openprocurement.tender.openua.procedure.state.question import UATenderQuestionStateMixin


class EUTenderQuestionState(UATenderQuestionStateMixin, BaseOpenEUTenderState):
    question_create_accreditations = (ACCR_4,)
