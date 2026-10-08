from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.state.award_claim import AwardClaimState
from openprocurement.tender.core.procedure.views.award import resolve_award
from openprocurement.tender.core.procedure.views.claim import (
    BaseClaimResource,
    resolve_claim,
)


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
    )
    def collection_post(self):
        return super().collection_post()
