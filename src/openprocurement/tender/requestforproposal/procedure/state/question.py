from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.core.procedure.state.question import (
    TenderQuestionStateMixin,
)
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RFPTenderState,
)


class RFPTenderQuestionState(TenderQuestionStateMixin, RFPTenderState):
    question_create_accreditations = (AccreditationLevel.ACCR_2,)

    question_operation_allowed_tender_statuses = None
