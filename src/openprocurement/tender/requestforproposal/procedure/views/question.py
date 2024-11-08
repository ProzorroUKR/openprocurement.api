from cornice.resource import resource

from openprocurement.tender.core.procedure.views.question import TenderQuestionResource
from openprocurement.tender.requestforproposal.procedure.state.question import (
    RequestForProposalTenderQuestionState,
)


@resource(
    name="requestForProposal:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType="requestForProposal",
    description="Tender questions",
)
class RequestForProposalTenderQuestionResource(TenderQuestionResource):
    state_class = RequestForProposalTenderQuestionState
