from openprocurement.tender.core.procedure.views.award_claim import AwardClaimResource
from openprocurement.tender.belowthreshold.procedure.state.award_claim import BelowThresholdAwardClaimState
from openprocurement.tender.core.procedure.validation import (
    unless_admins,
    validate_any_bid_owner,
    validate_input_data,
    validate_data_documents,
)
from openprocurement.tender.core.procedure.models.claim import PostClaim
from openprocurement.api.utils import json_view
from cornice.resource import resource


@resource(
    name="belowThreshold:Tender Award Claims",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="belowThreshold",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender award claims",
)
class BelowThresholdAwardClaimResource(AwardClaimResource):
    state_class = BelowThresholdAwardClaimState

    @json_view(
        content_type="application/json",
        permission="create_claim",
        validators=(
            unless_admins(
                validate_any_bid_owner()
            ),
            validate_input_data(PostClaim),
            validate_data_documents(route_key="claim", uid_key="id"),
        ),
    )
    def collection_post(self):
        return super().collection_post()
