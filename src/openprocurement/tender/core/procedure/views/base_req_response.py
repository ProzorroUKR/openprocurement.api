from logging import getLogger
from typing import Optional, List, Tuple

from pyramid.request import Request
from pyramid.security import Allow, Everyone, ALL_PERMISSIONS

from openprocurement.tender.core.procedure.utils import get_items
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.api.utils import context_unpack
from openprocurement.tender.core.procedure.utils import save_tender, set_item
from openprocurement.tender.core.procedure.serializers.req_response import RequirementResponseSerializer
from openprocurement.tender.core.procedure.state.base import BaseState


LOGGER = getLogger(__name__)


def resolve_req_response(request: Request, parent_obj_name: str) -> None:
    match_dict = request.matchdict
    if match_dict.get("requirement_response_id"):
        req_response_id = match_dict["requirement_response_id"]
        req_responses = get_items(request, request.validated[parent_obj_name], "requirementResponses", req_response_id)
        request.validated["requirement_response"] = req_responses[0]


class BaseReqResponseResource(TenderBaseResource):

    def __acl__(self) -> List[Tuple[str, str, str]]:
        return [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_req_response"),
            (Allow, "g:brokers", "edit_req_response"),
            (Allow, "g:Administrator", "edit_req_response"),  # wtf ???
            (Allow, "g:admins", ALL_PERMISSIONS),    # some tests use this, idk why
        ]

    serializer_class = RequirementResponseSerializer
    state_class: BaseState
    parent_obj_name: str

    def get_parent(self) -> dict:
        return self.request.validated[self.parent_obj_name]

    def collection_post(self) -> Optional[dict]:

        parent = self.get_parent()
        req_responses = self.request.validated["data"]
        if "requirementResponses" not in parent:
            parent["requirementResponses"] = []
        parent["requirementResponses"].extend(req_responses)

        self.state.on_post(req_responses)

        if save_tender(self.request, modified=False):
            for req_response in req_responses:
                self.LOGGER.info(
                    f"Created {self.parent_obj_name} requirement response {req_response['id']}",
                    extra=context_unpack(
                        self.request,
                        {"MESSAGE_ID": f"{self.parent_obj_name}_requirement_response_create"},
                        {"requirement_response_id": req_response['id']},
                    ),
                )
                self.request.response.status = 201

            return {"data": [self.serializer_class(rr).data for rr in req_responses]}

    def collection_get(self) -> dict:
        parent = self.get_parent()
        data = tuple(self.serializer_class(rr).data for rr in parent.get("requirementResponses", ""))
        return {"data": data}

    def get(self) -> dict:
        data = self.serializer_class(self.request.validated["requirement_response"]).data
        return {"data": data}

    def patch(self) -> Optional[dict]:
        updated_req_response = self.request.validated["data"]
        if not updated_req_response:
            return
        req_response = self.request.validated["requirement_response"]
        parent = self.get_parent()
        set_item(parent, "requirementResponses", req_response["id"], updated_req_response)
        self.state.on_patch(req_response, updated_req_response)

        if save_tender(self.request):
            self.LOGGER.info(
                f"Updated {self.parent_obj_name} requirement response {req_response['id']}",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": f"{self.parent_obj_name}_requirement_response_patch"}
                ),
            )
            return {"data": self.serializer_class(updated_req_response).data}

    def delete(self) -> Optional[dict]:
        parent = self.get_parent()
        req_response = self.request.validated["requirement_response"]

        parent["requirementResponses"].remove(req_response)
        if not parent["requirementResponses"]:
            del parent["requirementResponses"]

        if save_tender(self.request, modified=False):
            self.LOGGER.info(
                f"Deleted {self.parent_obj_name} requirement response {req_response['id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": f"{self.parent_obj_name}_requirement_response_delete"}),
            )
            return {"data": self.serializer_class(req_response).data}
