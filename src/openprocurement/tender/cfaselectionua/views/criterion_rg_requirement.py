# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.criterion_rg_requirement import TenderCriteriaRGRequirementResource


@optendersresource(
    name="closeFrameworkAgreementSelectionUA:Requirement Group Requirement",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
                    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
         "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender requirement group requirement",
)
class TenderCriteriaRGRequirementResource(TenderCriteriaRGRequirementResource):
    pass
