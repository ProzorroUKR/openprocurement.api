from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.core.procedure.state.question import (
    TenderQuestionStateMixin,
)
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RequestForProposalTenderState,
)


class RequestForProposalTenderQuestionState(TenderQuestionStateMixin, RequestForProposalTenderState):
    question_create_accreditations = (AccreditationLevel.ACCR_2,)
