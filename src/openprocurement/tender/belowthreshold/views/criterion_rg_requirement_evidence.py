# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.criterion_rg_requirement_evidence import (
    BaseTenderCriteriaRGRequirementEvidenceResource,
)
from openprocurement.tender.core.validation import (
    validate_eligible_evidence_data,
    validate_patch_eligible_evidence_data,
)
from openprocurement.tender.belowthreshold.validation import validate_operation_ecriteria_objects
from openprocurement.api.utils import json_view


@optendersresource(
    name="belowThreshold:Requirement Eligible Evidence",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
                    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
         "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType="belowThreshold",
    description="Tender requirement evidence",
)
class TenderCriteriaRGRequirementEvidenceResource(BaseTenderCriteriaRGRequirementEvidenceResource):
    @json_view(
        content_type="application/json",
        validators=(
            validate_operation_ecriteria_objects,
            validate_eligible_evidence_data,
        ),
        permission="edit_tender"
    )
    def collection_post(self):
        return super(TenderCriteriaRGRequirementEvidenceResource, self).collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            validate_operation_ecriteria_objects,
            validate_patch_eligible_evidence_data,
        ),
        permission="edit_tender"
    )
    def patch(self):
        return super(TenderCriteriaRGRequirementEvidenceResource, self).patch()

    @json_view(
        validators=(validate_operation_ecriteria_objects,),
        permission="edit_tender"
    )
    def delete(self):
        return super(TenderCriteriaRGRequirementEvidenceResource, self).delete()

