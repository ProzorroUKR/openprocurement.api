from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.core.procedure.state.question import TenderQuestionStateMixin
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState


class ESCOTenderQuestionState(TenderQuestionStateMixin, ESCOTenderState):
    question_operation_allowed_tender_statuses = ("active.tendering",)
    question_create_accreditations = (AccreditationLevel.ACCR_4,)
