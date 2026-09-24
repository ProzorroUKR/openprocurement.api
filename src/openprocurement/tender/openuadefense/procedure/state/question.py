from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.core.procedure.state.question import TenderQuestionStateMixin
from openprocurement.tender.openuadefense.procedure.state.tender import (
    OpenUADefenseTenderState,
)


class DefenseTenderQuestionState(TenderQuestionStateMixin, OpenUADefenseTenderState):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)

    question_operation_allowed_tender_statuses = ("active.tendering",)
