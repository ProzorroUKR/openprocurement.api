from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.competitiveordering.procedure.state.tender import (
    COTenderState,
)
from openprocurement.tender.core.procedure.state.question import (
    TenderQuestionStateMixin,
)


class COTenderQuestionStateMixin(TenderQuestionStateMixin):
    question_operation_allowed_tender_statuses = ("active.tendering",)


class COTenderQuestionState(COTenderQuestionStateMixin, COTenderState):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)
