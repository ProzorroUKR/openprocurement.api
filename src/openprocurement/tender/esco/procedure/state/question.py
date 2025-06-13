from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState
from openprocurement.tender.openua.procedure.state.question import (
    UATenderQuestionStateMixin,
)


class ESCOTenderQuestionState(UATenderQuestionStateMixin, ESCOTenderState):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)
