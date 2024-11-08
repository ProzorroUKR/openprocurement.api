from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.core.procedure.views.review_request import (
    TenderReviewRequestResource,
)
from openprocurement.tender.requestforproposal.procedure.state.review_request import (
    ReviewRequestState,
)

LOGGER = getLogger(__name__)


@resource(
    name="requestForProposal:Tender Review Request",
    collection_path="/tenders/{tender_id}/review_requests",
    path="/tenders/{tender_id}/review_requests/{review_request_id}",
    description="Tender review request",
    procurementMethodType="requestForProposal",
)
class RequestForProposalTenderReviewRequestResource(TenderReviewRequestResource):
    state_class = ReviewRequestState
