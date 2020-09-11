# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.criterion_rg_requirement import BaseTenderCriteriaRGRequirementResource
from openprocurement.tender.core.validation import (
    validate_requirement_data,
    validate_patch_requirement_data
)
from openprocurement.tender.belowthreshold.validation import validate_operation_ecriteria_objects
from openprocurement.api.utils import json_view


@optendersresource(
    name="belowThreshold:Requirement Group Requirement",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
                    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
         "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType="belowThreshold",
    description="Tender requirement group requirement",
)
class TenderCriteriaRGRequirementResource(BaseTenderCriteriaRGRequirementResource):
    @json_view(
        content_type="application/json",
        validators=(
            validate_operation_ecriteria_objects,
            validate_requirement_data,
        ),
        permission="edit_tender"
    )
    def collection_post(self):
        return super(TenderCriteriaRGRequirementResource, self).collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            validate_operation_ecriteria_objects,
            validate_patch_requirement_data,
        ),
        permission="edit_tender"
    )
    def patch(self):
        return super(TenderCriteriaRGRequirementResource, self).patch()

