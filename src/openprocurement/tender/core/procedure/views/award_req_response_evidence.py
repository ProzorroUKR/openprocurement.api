from typing import Optional

from openprocurement.api.procedure.validation import (
    validate_request_by_state,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.state.req_response_evidence import (
    AwardReqResponseEvidenceState,
)
from openprocurement.tender.core.procedure.views.award_req_response import (
    resolve_award,
    resolve_req_response,
)
from openprocurement.tender.core.procedure.views.base_req_response_evidence import (
    BaseReqResponseEvidenceResource,
    resolve_evidence,
)


class AwardReqResponseEvidenceResource(BaseReqResponseEvidenceResource):
    state_class = AwardReqResponseEvidenceState
    parent_obj_name = "award"

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_award(request)
            resolve_req_response(request, self.parent_obj_name)
            resolve_evidence(request)

    @json_view(
        content_type="application/json",
        validators=(validate_request_by_state,),
        permission="create_rr_evidence",
    )
    def collection_post(self) -> Optional[dict]:
        return super().collection_post()

    @json_view(permission="view_tender")
    def collection_get(self) -> dict:
        return super().collection_get()

    @json_view(permission="view_tender")
    def get(self) -> dict:
        return super().get()

    @json_view(
        content_type="application/json",
        validators=(validate_request_by_state,),
        permission="edit_rr_evidence",
    )
    def patch(self) -> Optional[dict]:
        return super().patch()

    @json_view(
        validators=(validate_request_by_state,),
        permission="edit_rr_evidence",
    )
    def delete(self) -> Optional[dict]:
        return super().delete()
