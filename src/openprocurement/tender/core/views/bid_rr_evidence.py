# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.tender.core.validation import (
    validate_evidence_data,
    validate_patch_evidence_data,
    validate_operation_ecriteria_objects,
    validate_view_requirement_responses,
)
from openprocurement.tender.core.views.requirement_response_evidence import BaseRequirementResponseEvidenceResource


class BaseBidRequirementResponseEvidenceResource(BaseRequirementResponseEvidenceResource):

    @json_view(
        content_type="application/json",
        validators=(
            validate_operation_ecriteria_objects,
            validate_evidence_data,
        ),
        permission="edit_bid",
    )
    def collection_post(self):
        return super(BaseBidRequirementResponseEvidenceResource, self).collection_post()

    @json_view(permission="view_tender",  validators=(validate_view_requirement_responses,))
    def collection_get(self):
        return super(BaseBidRequirementResponseEvidenceResource, self).collection_get()

    @json_view(permission="view_tender",  validators=(validate_view_requirement_responses,))
    def get(self):
        return super(BaseBidRequirementResponseEvidenceResource, self).get()

    @json_view(
        content_type="application/json",
        validators=(
            validate_operation_ecriteria_objects,
            validate_patch_evidence_data,
        ),
        permission="edit_bid",
    )
    def patch(self):
        return super(BaseBidRequirementResponseEvidenceResource, self).patch()

    @json_view(
        validators=(
            validate_operation_ecriteria_objects,
        ),
        permission="edit_bid",
    )
    def delete(self):
        return super(BaseBidRequirementResponseEvidenceResource, self).delete()
