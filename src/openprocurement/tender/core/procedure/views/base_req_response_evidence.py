from typing import Optional, List, Tuple
from logging import getLogger

from pyramid.request import Request
from pyramid.security import Allow, Everyone, ALL_PERMISSIONS

from openprocurement.tender.core.procedure.utils import get_items
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.api.utils import context_unpack
from openprocurement.tender.core.procedure.utils import save_tender, set_item
from openprocurement.tender.core.procedure.serializers.base import BaseSerializer
from openprocurement.tender.core.procedure.state.req_response_evidence import ReqResponseEvidenceState


LOGGER = getLogger(__name__)


def resolve_evidence(request: Request) -> None:
    match_dict = request.matchdict
    if match_dict.get("evidence_id"):
        evidence_id = match_dict["evidence_id"]
        evidences = get_items(request, request.validated["requirement_response"], "evidences", evidence_id)
        request.validated["evidence"] = evidences[0]


class BaseReqResponseEvidenceResource(TenderBaseResource):

    def __acl__(self) -> List[Tuple[str, str, str]]:
        return [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_rr_evidence"),
            (Allow, "g:brokers", "edit_rr_evidence"),
            (Allow, "g:Administrator", "edit_rr_evidence"),  # wtf ???
            (Allow, "g:admins", ALL_PERMISSIONS),    # some tests use this, idk why
        ]

    serializer_class = BaseSerializer
    state_class: ReqResponseEvidenceState
    parent_obj_name: str

    def collection_post(self) -> Optional[dict]:

        req_response = self.request.validated["requirement_response"]
        evidence = self.request.validated["data"]
        if "evidences" not in req_response:
            req_response["evidences"] = []
        req_response["evidences"].append(evidence)

        self.state.on_post(evidence)
        if save_tender(self.request):
            self.LOGGER.info(
                f"Created {self.parent_obj_name} requirement response evidence {evidence['id']}",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": f"{self.parent_obj_name}_requirement_response_evidence_create"},
                    {"evidence_id": evidence["id"]},
                ),
            )
            self.request.response.status = 201
            return {"data": self.serializer_class(evidence).data}

    def collection_get(self) -> dict:
        req_response = self.request.validated["requirement_response"]
        data = tuple(self.serializer_class(evidence).data for evidence in req_response.get("evidences", ""))
        return {"data": data}

    def get(self) -> dict:
        data = self.serializer_class(self.request.validated["evidence"]).data
        return {"data": data}

    def patch(self) -> Optional[dict]:
        updated_evidence = self.request.validated["data"]
        if not updated_evidence:
            return
        evidence = self.request.validated["evidence"]
        req_response = self.request.validated["requirement_response"]
        set_item(req_response, "evidences", evidence["id"], updated_evidence)
        self.state.on_patch(evidence, updated_evidence)

        if save_tender(self.request):
            self.LOGGER.info(
                f"Updated {self.parent_obj_name} requirement response evidence {evidence['id']}",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": f"{self.parent_obj_name}_requirement_response_evidence_patch"},
                ),
            )
            return {"data": self.serializer_class(updated_evidence).data}

    def delete(self) -> Optional[dict]:
        req_response = self.request.validated["requirement_response"]
        evidence = self.request.validated["evidence"]

        req_response["evidences"].remove(evidence)
        if not req_response["evidences"]:
            del req_response["evidences"]

        if save_tender(self.request, modified=False):
            self.LOGGER.info(
                f"Deleted {self.parent_obj_name} requirement response evidence {evidence['id']}",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": f"{self.parent_obj_name}_requirement_response_evidence_delete"}
                ),
            )
            return {"data": self.serializer_class(evidence).data}
