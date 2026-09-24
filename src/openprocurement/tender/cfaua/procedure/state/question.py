from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.core.procedure.state.question import TenderQuestionStateMixin


class CFAUATenderQuestionState(TenderQuestionStateMixin, CFAUATenderState):
    question_operation_allowed_tender_statuses = ("active.tendering",)
    question_create_accreditations = (AccreditationLevel.ACCR_4,)
