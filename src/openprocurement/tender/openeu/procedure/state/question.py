from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.core.procedure.state.question import TenderQuestionStateMixin
from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState


class EUTenderQuestionState(TenderQuestionStateMixin, BaseOpenEUTenderState):
    question_operation_allowed_tender_statuses = ("active.tendering",)
    question_create_accreditations = (AccreditationLevel.ACCR_4,)
