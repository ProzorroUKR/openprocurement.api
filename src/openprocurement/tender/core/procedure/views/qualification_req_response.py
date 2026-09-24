from typing import Optional

from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    validate_request_by_state,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.state.req_response import (
    QualificationReqResponseState,
)
from openprocurement.tender.core.procedure.views.base_req_response import (
    BaseReqResponseResource,
    resolve_req_response,
)
from openprocurement.tender.core.procedure.views.qualification import (
    resolve_qualification,
)


@resource(
    name="Qualification Requirement Response",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/requirement_responses",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/requirement_responses/{requirement_response_id}",
    description="Tender qualification requirement responses",
)
class QualificationReqResponseResource(BaseReqResponseResource):
    state_class = QualificationReqResponseState
    parent_obj_name = "qualification"

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_qualification(request)
            resolve_req_response(request, self.parent_obj_name)

    @json_view(
        content_type="application/json",
        validators=(validate_request_by_state,),
        permission="create_req_response",
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
        permission="edit_req_response",
    )
    def patch(self) -> Optional[dict]:
        return super().patch()

    @json_view(
        validators=(validate_request_by_state,),
        permission="edit_req_response",
    )
    def delete(self) -> Optional[dict]:
        return super().delete()
