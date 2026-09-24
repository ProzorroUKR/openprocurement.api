from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.question import TenderQuestionStateMixin


class QuestionState(TenderQuestionStateMixin, TenderState):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)

    question_operation_allowed_tender_statuses = ("active.tendering",)
