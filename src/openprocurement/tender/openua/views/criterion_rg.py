# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.criterion_rg import BaseTenderCriteriaRGResource


@optendersresource(
    name="aboveThresholdUA:Criteria Requirement Group",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender criteria requirement group",
)
class TenderUaCriteriaRGResource(BaseTenderCriteriaRGResource):
    pass
