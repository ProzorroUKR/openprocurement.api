from typing import Optional

from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.models.req_response import RequirementResponse, PatchRequirementResponse
from openprocurement.tender.core.procedure.state.req_response import BidReqResponseState
from openprocurement.tender.core.procedure.validation import (
    unless_administrator,
    validate_item_owner,
    validate_input_data,
    validate_patch_data_simple,
    validate_operation_ecriteria_on_tender_status,
    validate_view_requirement_responses,
)
from openprocurement.tender.core.procedure.views.bid import resolve_bid
from openprocurement.tender.core.procedure.views.base_req_response import BaseReqResponseResource, resolve_req_response


class BidReqResponseResource(BaseReqResponseResource):
    state_class = BidReqResponseState
    parent_obj_name = "bid"

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_bid(request)
            resolve_req_response(request, self.parent_obj_name)

    @json_view(
        content_type="application/json",
        validators=(
                unless_administrator(validate_item_owner("bid")),
                validate_operation_ecriteria_on_tender_status,
                validate_input_data(RequirementResponse, allow_bulk=True),
        ),
        permission="create_req_response",
    )
    def collection_post(self) -> Optional[dict]:
        return super().collection_post()

    @json_view(permission="view_tender", validators=(validate_view_requirement_responses,))
    def collection_get(self) -> dict:
        return super().collection_get()

    @json_view(permission="view_tender", validators=(validate_view_requirement_responses,))
    def get(self) -> dict:
        return super().get()

    @json_view(
        content_type="application/json",
        validators=(
                unless_administrator(validate_item_owner("bid")),
                validate_operation_ecriteria_on_tender_status,
                validate_input_data(PatchRequirementResponse),
                validate_patch_data_simple(RequirementResponse, "requirement_response"),
        ),
        permission="edit_req_response",
    )
    def patch(self) -> Optional[dict]:
        return super().patch()

    @json_view(
        validators=(
                unless_administrator(validate_item_owner("bid")),
                validate_operation_ecriteria_on_tender_status,
        ),
        permission="edit_req_response",
    )
    def delete(self) -> Optional[dict]:
        return super().delete()
