# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.criterion_rg_requirement import BaseTenderCriteriaRGRequirementResource
from openprocurement.tender.open.constants import ABOVE_THRESHOLD


# @optendersresource(
#     name=f"{ABOVE_THRESHOLD}:Requirement Group Requirement",
#     collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}/requirements",
#     path="/tenders/{tender_id}/criteria/{criterion_id}/"
#          "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
#     procurementMethodType=ABOVE_THRESHOLD,
#     description="Tender requirement group requirement",
# )
# class TenderUaCriteriaRGRequirementResource(BaseTenderCriteriaRGRequirementResource):
#     pass
