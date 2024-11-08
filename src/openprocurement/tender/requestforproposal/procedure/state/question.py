from openprocurement.api.auth import ACCR_2
from openprocurement.tender.core.procedure.state.question import (
    TenderQuestionStateMixin,
)
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RequestForProposalTenderState,
)


class RequestForProposalTenderQuestionState(TenderQuestionStateMixin, RequestForProposalTenderState):
    question_create_accreditations = (ACCR_2,)
