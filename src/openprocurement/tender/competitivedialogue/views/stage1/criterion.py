# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.criterion import BaseTenderCriteriaResource
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE


@optendersresource(
    name="{}:Tender Criteria".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU criteria",
)
class CDEUCriteriaResource(BaseTenderCriteriaResource):
    pass


@optendersresource(
    name="{}:Tender Criteria".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA criteria",
)
class CDUACriteriaResource(BaseTenderCriteriaResource):
    pass

