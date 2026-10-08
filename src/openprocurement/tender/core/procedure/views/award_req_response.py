from typing import Optional

from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.views.award import resolve_award
from openprocurement.tender.core.procedure.views.base_req_response import (
    BaseReqResponseResource,
    resolve_req_response,
)


class AwardReqResponseResource(BaseReqResponseResource):
    parent_obj_name = "award"

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_award(request)
            resolve_req_response(request, self.parent_obj_name)

    @json_view(
        content_type="application/json",
        permission="create_req_response",
    )
    def collection_post(self) -> Optional[dict]:
        self.state.validate_req_response_post_request()
        return super().collection_post()

    @json_view(permission="view_tender")
    def collection_get(self) -> dict:
        return super().collection_get()

    @json_view(permission="view_tender")
    def get(self) -> dict:
        return super().get()

    @json_view(
        content_type="application/json",
        permission="edit_req_response",
    )
    def patch(self) -> Optional[dict]:
        self.state.validate_req_response_patch_request()
        return super().patch()

    @json_view(
        permission="edit_req_response",
    )
    def delete(self) -> Optional[dict]:
        self.state.validate_req_response_delete_request()
        return super().delete()
