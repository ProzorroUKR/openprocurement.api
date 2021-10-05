# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.auction import TenderAuctionResource as TenderEUAuctionResource


# @optendersresource(
#     name="esco:Tender Auction",
#     collection_path="/tenders/{tender_id}/auction",
#     path="/tenders/{tender_id}/auction/{auction_lot_id}",
#     procurementMethodType="esco",
#     description="Tender ESCO Auction data",
# )
class TenderESCOAuctionResource(TenderEUAuctionResource):
    """ Tender ESCO Auction Resource """
