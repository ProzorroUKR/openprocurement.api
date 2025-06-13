from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.openua.procedure.state.question import (
    UATenderQuestionStateMixin,
)
from openprocurement.tender.openuadefense.procedure.state.tender import (
    OpenUADefenseTenderState,
)


class DefenseTenderQuestionState(UATenderQuestionStateMixin, OpenUADefenseTenderState):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)
