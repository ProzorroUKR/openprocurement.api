from openprocurement.tender.core.procedure.utils import get_items
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.serializers.complaint import TenderComplaintSerializer, ComplaintSerializer
from openprocurement.tender.core.procedure.views.qualification import resolve_qualification
from openprocurement.tender.core.procedure.views.claim import (
    resolve_claim,
)
from openprocurement.tender.core.procedure.models.claim import PostClaim
from openprocurement.tender.core.procedure.views.claim import BaseClaimResource
from openprocurement.tender.core.procedure.state.qualification_claim import QualificationClaimState
from openprocurement.tender.core.procedure.validation import (
    unless_admins,
    validate_any_bid_owner,
    validate_input_data,
    validate_data_documents,
)


class QualificationClaimResource(BaseClaimResource):
    serializer_class = TenderComplaintSerializer
    state_class = QualificationClaimState
    item_name = "qualification"

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_qualification(request)
            # resolve bid related to qualification
            bid_id = request.validated["qualification"]["bidID"]
            bids = get_items(request, request.validated["tender"], "bids", bid_id)
            request.validated["bid"] = bids[0]
            resolve_claim(request, context="qualification")

    @json_view(
        content_type="application/json",
        permission="create_claim",
        validators=(
            validate_input_data(PostClaim),
            unless_admins(
                validate_any_bid_owner(statuses=("active", "unsuccessful", "invalid.pre-qualification"))
            ),
            validate_data_documents(route_key="claim_id", uid_key="id"),
        ),
    )
    def collection_post(self):
        return super().collection_post()