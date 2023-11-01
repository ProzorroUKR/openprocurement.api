from openprocurement.api.auth import ACCR_4
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState
from openprocurement.tender.openua.procedure.state.question import UATenderQuestionStateMixin


class ESCOTenderQuestionState(UATenderQuestionStateMixin, ESCOTenderState):
    question_create_accreditations = (ACCR_4,)
