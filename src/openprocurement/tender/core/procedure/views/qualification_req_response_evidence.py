from typing import Optional

from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.validation import (
    unless_administrator,
    validate_item_owner,
    validate_input_data,
    validate_patch_data_simple,
    validate_operation_qualification_requirement_response,
)
from openprocurement.tender.core.procedure.models.evidence import Evidence, PatchEvidence
from openprocurement.tender.core.procedure.views.qualification_req_response import (
    resolve_qualification,
    resolve_req_response,
)
from openprocurement.tender.core.procedure.views.base_req_response_evidence import (
    BaseReqResponseEvidenceResource,
    resolve_evidence,
)
from openprocurement.tender.core.procedure.state.req_response_evidence import QualificationReqResponseEvidenceState


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
        validators=(
                unless_administrator(validate_item_owner("tender")),
                validate_operation_qualification_requirement_response,
                validate_input_data(Evidence),
        ),
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
        validators=(
                unless_administrator(validate_item_owner("tender")),
                validate_operation_qualification_requirement_response,
                validate_input_data(PatchEvidence),
                validate_patch_data_simple(Evidence, "evidence"),
        ),
        permission="edit_rr_evidence",
    )
    def patch(self) -> Optional[dict]:
        return super().patch()

    @json_view(
        validators=(
                unless_administrator(validate_item_owner("tender")),
                validate_operation_qualification_requirement_response,
        ),
        permission="edit_rr_evidence",
    )
    def delete(self) -> Optional[dict]:
        return super().delete()
