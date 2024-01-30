from cornice.resource import resource
from logging import getLogger

from openprocurement.tender.core.procedure.views.review_request import TenderReviewRequestResource
from openprocurement.tender.belowthreshold.procedure.state.review_request import ReviewRequestState

LOGGER = getLogger(__name__)


@resource(
    name="belowThreshold:Tender Review Request",
    collection_path="/tenders/{tender_id}/review_requests",
    path="/tenders/{tender_id}/review_requests/{review_request_id}",
    description="Tender review request",
    procurementMethodType="belowThreshold",
)
class BelowThresholdTenderReviewRequestResource(TenderReviewRequestResource):
    state_class = ReviewRequestState
