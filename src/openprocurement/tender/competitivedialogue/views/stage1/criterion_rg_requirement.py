# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.criterion_rg_requirement import BaseTenderCriteriaRGRequirementResource
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE


@optendersresource(
    name="{}:Requirement Group Requirement".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
                    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
         "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU requirement group requirement",
)
class CDEUCriteriaRGRequirementResource(BaseTenderCriteriaRGRequirementResource):
    pass


@optendersresource(
    name="{}:Requirement Group Requirement".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
                    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
         "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA requirement group requirement",
)
class CDUACriteriaRGRequirementResource(BaseTenderCriteriaRGRequirementResource):
    pass
