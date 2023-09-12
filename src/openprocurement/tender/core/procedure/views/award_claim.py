from openprocurement.tender.core.procedure.views.award import resolve_award
from openprocurement.tender.core.procedure.views.claim import (
    resolve_claim,
)
from openprocurement.tender.core.procedure.models.claim import PostClaim
from openprocurement.tender.core.procedure.views.claim import BaseClaimResource
from openprocurement.tender.core.procedure.state.award_claim import AwardClaimState
from openprocurement.tender.core.procedure.validation import (
    unless_admins,
    validate_any_bid_owner,
    validate_input_data,
    validate_data_documents,
)
from openprocurement.api.utils import json_view


class AwardClaimResource(BaseClaimResource):
    state_class = AwardClaimState
    item_name = "award"

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_award(request)
            resolve_claim(request, context="award")

    @json_view(
        content_type="application/json",
        permission="create_claim",
        validators=(
            unless_admins(
                validate_any_bid_owner(statuses=("active",))
            ),
            validate_input_data(PostClaim),
            validate_data_documents(route_key="claim", uid_key="id"),
        ),
    )
    def collection_post(self):
        return super().collection_post()
