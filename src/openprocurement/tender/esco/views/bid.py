# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.bid import TenderBidResource as TenderEUBidResource


# @optendersresource(
#     name="esco:Tender Bids",
#     collection_path="/tenders/{tender_id}/bids",
#     path="/tenders/{tender_id}/bids/{bid_id}",
#     procurementMethodType="esco",
#     description="Tender ESCO bids",
# )
class TenderESCOBidResource(TenderEUBidResource):
    """ Tender ESCO Bid Resource """
