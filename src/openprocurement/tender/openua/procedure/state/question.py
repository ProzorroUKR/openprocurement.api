from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.core.procedure.state.question import (
    TenderQuestionStateMixin,
)
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


class OpenUATenderQuestionStateMixin(TenderQuestionStateMixin):
    question_create_accreditations = None


class OpenUATenderQuestionState(OpenUATenderQuestionStateMixin, OpenUATenderState):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)
