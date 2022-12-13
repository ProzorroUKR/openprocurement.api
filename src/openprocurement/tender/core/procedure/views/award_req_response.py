from typing import Optional

from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.models.req_response import RequirementResponse, PatchRequirementResponse
from openprocurement.tender.core.procedure.state.req_response import AwardReqResponseState
from openprocurement.tender.core.procedure.validation import (
    unless_administrator,
    validate_item_owner,
    validate_input_data,
    validate_patch_data_simple,
    validate_operation_award_requirement_response,
)
from openprocurement.tender.core.procedure.views.award import resolve_award
from openprocurement.tender.core.procedure.views.base_req_response import BaseReqResponseResource, resolve_req_response


class AwardReqResponseResource(BaseReqResponseResource):
    state_class = AwardReqResponseState
    parent_obj_name = "award"

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_award(request)
            resolve_req_response(request, self.parent_obj_name)

    @json_view(
        content_type="application/json",
        validators=(
                validate_item_owner("tender"),
                validate_operation_award_requirement_response,
                validate_input_data(RequirementResponse, allow_bulk=True),
        ),
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
        validators=(
                validate_item_owner("tender"),
                validate_operation_award_requirement_response,
                validate_input_data(PatchRequirementResponse),
                validate_patch_data_simple(RequirementResponse, "requirement_response"),
        ),
        permission="edit_req_response",
    )
    def patch(self) -> Optional[dict]:
        return super().patch()

    @json_view(
        validators=(
                unless_administrator(validate_item_owner("tender")),
                validate_operation_award_requirement_response,
        ),
        permission="edit_req_response",
    )
    def delete(self) -> Optional[dict]:
        return super().delete()
