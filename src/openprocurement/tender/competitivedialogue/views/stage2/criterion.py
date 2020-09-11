# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.criterion import BaseTenderCriteriaResource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE


@optendersresource(
    name="{}:Tender Criteria".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU criteria",
)
class CDEUCriteriaResource(BaseTenderCriteriaResource):
    pass


@optendersresource(
    name="{}:Tender Criteria".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage 2 UA criteria",
)
class CDUACriteriaResource(BaseTenderCriteriaResource):
    pass

