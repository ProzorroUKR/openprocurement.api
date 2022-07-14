from openprocurement.api.auth import ACCR_4
from openprocurement.tender.openua.procedure.state.question import UATenderQuestionStateMixin
from openprocurement.tender.openuadefense.procedure.state.tender import OpenUADefenseTenderState


class DefenseTenderQuestionState(UATenderQuestionStateMixin, OpenUADefenseTenderState):
    create_accreditations = (ACCR_4,)
