# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.criterion_rg_requirement import TenderCriteriaRGRequirementResource


from openprocurement.tender.core.validation import (
    validate_patch_requirement_data,
    validate_put_requirement_objects,
)

from openprocurement.api.utils import json_view

# @optendersresource(
#     name="closeFrameworkAgreementSelectionUA:Requirement Group Requirement",
#     collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
#                     "requirement_groups/{requirement_group_id}/requirements",
#     path="/tenders/{tender_id}/criteria/{criterion_id}/"
#          "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
#     procurementMethodType="closeFrameworkAgreementSelectionUA",
#     description="Tender requirement group requirement",
# )
class TenderCriteriaRGRequirementResource(TenderCriteriaRGRequirementResource):
    @json_view(
        content_type="application/json",
        validators=(
                validate_put_requirement_objects,
                validate_patch_requirement_data,
        ),
        permission="edit_tender"
    )
    def put(self):
        return super(TenderCriteriaRGRequirementResource, self).put()
