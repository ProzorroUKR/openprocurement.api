# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.criterion_rg import BaseTenderCriteriaRGResource
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE


@optendersresource(
    name="{}:Criteria Requirement Group".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU requirement group",
)
class CDEUCriteriaRGResource(BaseTenderCriteriaRGResource):
    pass


@optendersresource(
    name="{}:Criteria Requirement Group".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA requirement group",
)
class CDUACriteriaRGResource(BaseTenderCriteriaRGResource):
    pass
