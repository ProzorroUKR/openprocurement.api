# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.lot import TenderUaLotResource as TenderLotResource


# @optendersresource(
#     name="aboveThresholdUA.defense:Tender Lots",
#     collection_path="/tenders/{tender_id}/lots",
#     path="/tenders/{tender_id}/lots/{lot_id}",
#     procurementMethodType="aboveThresholdUA.defense",
#     description="Tender Ua lots",
# )
class TenderUaLotResource(TenderLotResource):
    pass
