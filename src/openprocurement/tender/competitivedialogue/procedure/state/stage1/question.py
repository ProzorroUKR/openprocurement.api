from openprocurement.api.auth import ACCR_4
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import TenderDetailsState
from openprocurement.tender.openua.procedure.state.question import UATenderQuestionStateMixin


class Stage1TenderQuestionState(UATenderQuestionStateMixin, TenderDetailsState):
    create_accreditations = (ACCR_4,)
