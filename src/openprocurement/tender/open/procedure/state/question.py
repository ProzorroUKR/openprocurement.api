from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.core.procedure.state.question import (
    TenderQuestionStateMixin,
)
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class OpenTenderQuestionStateMixin(TenderQuestionStateMixin):
    question_create_accreditations = None


class OpenTenderQuestionState(OpenTenderQuestionStateMixin, OpenTenderState):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)
