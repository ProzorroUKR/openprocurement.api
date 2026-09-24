from openprocurement.tender.core.procedure.state.question import TenderQuestionStateMixin
from openprocurement.tender.openuadefense.procedure.state.tender import (
    DefenseTenderState,
)


class DefenseTenderQuestionState(TenderQuestionStateMixin, DefenseTenderState):
    pass
