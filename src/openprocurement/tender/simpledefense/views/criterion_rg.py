# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.criterion_rg import BaseTenderCriteriaRGResource


# @optendersresource(
#     name="simple.defense:Criteria Requirement Group",
#     collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
#     path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
#     procurementMethodType="simple.defense",
#     description="Tender simple.defense criteria requirement group",
# )
class TenderSimpleDefCriteriaRGResource(BaseTenderCriteriaRGResource):
    pass
