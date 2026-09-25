from typing import Optional

from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.state.req_response_evidence import (
    QualificationReqResponseEvidenceState,
)
from openprocurement.tender.core.procedure.views.base_req_response_evidence import (
    BaseReqResponseEvidenceResource,
    resolve_evidence,
)
from openprocurement.tender.core.procedure.views.qualification_req_response import (
    resolve_qualification,
    resolve_req_response,
)


@resource(
    name="Qualification Requirement Response Evidence",
    collection_path=(
        "/tenders/{tender_id}/qualifications/{qualification_id}"
        "/requirement_responses/{requirement_response_id}/evidences"
    ),
    path=(
        "/tenders/{tender_id}/qualifications/{qualification_id}/"
        "requirement_responses/{requirement_response_id}/evidences/{evidence_id}"
    ),
    description="Tender qualification evidences",
)
class QualificationReqResponseEvidenceResource(BaseReqResponseEvidenceResource):
    state_class = QualificationReqResponseEvidenceState
    parent_obj_name = "qualification"

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_qualification(request)
            resolve_req_response(request, self.parent_obj_name)
            resolve_evidence(request)

    @json_view(
        content_type="application/json",
        permission="create_rr_evidence",
    )
    def collection_post(self) -> Optional[dict]:
        self.state.validate_req_response_evidence_post_request()
        return super().collection_post()

    @json_view(permission="view_tender")
    def collection_get(self) -> dict:
        return super().collection_get()

    @json_view(permission="view_tender")
    def get(self) -> dict:
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
