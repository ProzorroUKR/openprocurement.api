from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.core.procedure.state.question import (
    TenderQuestionStateMixin,
)
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


class UATenderQuestionStateMixin(TenderQuestionStateMixin):
    question_operation_allowed_tender_statuses = ("active.tendering",)


class UATenderQuestionState(UATenderQuestionStateMixin, OpenUATenderState):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)
