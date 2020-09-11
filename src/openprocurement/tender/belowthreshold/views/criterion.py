# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.criterion import BaseTenderCriteriaResource
from openprocurement.tender.core.validation import validate_criterion_data, validate_patch_criterion_data
from openprocurement.tender.belowthreshold.validation import validate_operation_ecriteria_objects
from openprocurement.api.utils import json_view


@optendersresource(
    name="belowThreshold:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType="belowThreshold",
    description="Tender criteria",
)
class TenderCriteriaResource(BaseTenderCriteriaResource):
    @json_view(
        content_type="application/json",
        validators=(
            validate_operation_ecriteria_objects,
            validate_criterion_data,
        ),
        permission="edit_tender"
    )
    def collection_post(self):
        return super(TenderCriteriaResource, self).collection_post()

    @json_view(
        content_type="application/json",
        validators=(
                validate_operation_ecriteria_objects,
                validate_patch_criterion_data,
        ),
        permission="edit_tender"
    )
    def patch(self):
        return super(TenderCriteriaResource, self).patch()
