from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.belowthreshold.procedure.state.review_request import (
    ReviewRequestState,
)
from openprocurement.tender.core.procedure.views.review_request import (
    TenderReviewRequestResource,
)

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
