# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openuadefense.views.bid import TenderUABidResource


# @optendersresource(
#     name="simple.defense:Tender Bids",
#     collection_path="/tenders/{tender_id}/bids",
#     path="/tenders/{tender_id}/bids/{bid_id}",
#     procurementMethodType="simple.defense",
#     description="Tender simple.defense bids",
# )
class TenderSimpleBidBidResource(TenderUABidResource):
    pass
