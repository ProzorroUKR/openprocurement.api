from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.views.review_request import TenderReviewRequestResource
from openprocurement.tender.core.procedure.models.review_request import PatchInspectorReviewRequest, ReviewRequest
from openprocurement.tender.belowthreshold.procedure.state.review_request import ReviewRequestState
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    validate_patch_data,
)
from cornice.resource import resource
from logging import getLogger

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

    @json_view(
        content_type="application/json",
        permission="edit_review_request",  # inspectors
        validators=(
            validate_input_data(PatchInspectorReviewRequest),
            validate_patch_data(ReviewRequest, item_name="review_request"),
        ),
    )
    def patch(self):
        return super().patch()
