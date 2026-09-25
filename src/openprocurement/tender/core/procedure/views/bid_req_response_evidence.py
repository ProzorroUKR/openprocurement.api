from typing import Optional

from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.state.req_response_evidence import (
    BidReqResponseEvidenceState,
)
from openprocurement.tender.core.procedure.views.base_req_response_evidence import (
    BaseReqResponseEvidenceResource,
    resolve_evidence,
)
from openprocurement.tender.core.procedure.views.bid_req_response import (
    resolve_bid,
    resolve_req_response,
)


class BidReqResponseEvidenceResource(BaseReqResponseEvidenceResource):
    state_class = BidReqResponseEvidenceState
    parent_obj_name = "bid"

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_bid(request)
            resolve_req_response(request, self.parent_obj_name)
            resolve_evidence(request)

    @json_view(
        content_type="application/json",
        permission="create_rr_evidence",
    )
    def collection_post(self) -> Optional[dict]:
        self.state.validate_req_response_evidence_post_request()
        return super().collection_post()

    @json_view(
        permission="view_tender",
    )
    def collection_get(self) -> dict:
        self.state.validate_req_response_evidence_get_request()
        return super().collection_get()

    @json_view(
        permission="view_tender",
    )
    def get(self) -> dict:
        self.state.validate_req_response_evidence_get_request()
        return super().get()

    @json_view(
        content_type="application/json",
        permission="edit_rr_evidence",
    )
    def patch(self) -> Optional[dict]:
        self.state.validate_req_response_evidence_patch_request()
        return super().patch()

    @json_view(
        permission="edit_rr_evidence",
    )
    def delete(self) -> Optional[dict]:
        self.state.validate_req_response_evidence_delete_request()
        return super().delete()
