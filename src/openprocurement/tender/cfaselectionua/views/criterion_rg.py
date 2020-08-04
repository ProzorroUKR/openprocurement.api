# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.criterion_rg import TenderCriteriaRGResource


@optendersresource(
    name="closeFrameworkAgreementSelectionUA:Criteria Requirement Group",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender criteria requirement group",
)
class TenderCriteriaRGResource(TenderCriteriaRGResource):
    pass
