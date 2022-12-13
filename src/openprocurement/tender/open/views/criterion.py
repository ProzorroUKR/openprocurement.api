# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.criterion import BaseTenderCriteriaResource
from openprocurement.tender.open.constants import ABOVE_THRESHOLD


# @optendersresource(
#     name=f"{ABOVE_THRESHOLD}:Tender Criteria",
#     collection_path="/tenders/{tender_id}/criteria",
#     path="/tenders/{tender_id}/criteria/{criterion_id}",
#     procurementMethodType=ABOVE_THRESHOLD,
#     description="Tender criteria",
# )
# class TenderUaCriteriaResource(BaseTenderCriteriaResource):
#     pass

