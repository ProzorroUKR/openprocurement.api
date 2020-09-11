# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.criterion_rg import BaseTenderCriteriaRGResource
from openprocurement.tender.core.validation import (
    validate_requirement_group_data,
    validate_patch_requirement_group_data,
)
from openprocurement.tender.belowthreshold.validation import validate_operation_ecriteria_objects
from openprocurement.api.utils import json_view


@optendersresource(
    name="belowThreshold:Criteria Requirement Group",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType="belowThreshold",
    description="Tender criteria requirement group",
)
class TenderCriteriaRGResource(BaseTenderCriteriaRGResource):
    @json_view(
        content_type="application/json",
        validators=(
            validate_operation_ecriteria_objects,
            validate_requirement_group_data,
        ),
        permission="edit_tender"
    )
    def collection_post(self):
        return super(TenderCriteriaRGResource, self).collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            validate_operation_ecriteria_objects,
            validate_patch_requirement_group_data,
        ),
        permission="edit_tender"
    )
    def patch(self):
        return super(TenderCriteriaRGResource, self).patch()
