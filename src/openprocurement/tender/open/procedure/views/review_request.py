from cornice.resource import resource

from openprocurement.tender.core.procedure.views.review_request import TenderReviewRequestResource
from openprocurement.tender.open.constants import BELOW_THRESHOLD, OPEN_ROUTE_PREFIX, REQUEST_FOR_PROPOSAL
from openprocurement.tender.open.procedure.state.review_request import (
    BelowThresholdReviewRequestState,
    RFPReviewRequestState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Review Request",
    collection_path="/tenders/{tender_id}/review_requests",
    path="/tenders/{tender_id}/review_requests/{review_request_id}",
    description="Tender review request",
    procurementMethodType=[BELOW_THRESHOLD, REQUEST_FOR_PROPOSAL],
)
class OpenTenderReviewRequestResource(TenderReviewRequestResource):
    state_classes = {
        BELOW_THRESHOLD: BelowThresholdReviewRequestState,
        REQUEST_FOR_PROPOSAL: RFPReviewRequestState,
    }
