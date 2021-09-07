# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource

from openprocurement.tender.openuadefense.views.auction import TenderUaAuctionResource


# @optendersresource(
#     name="simple.defense:Auction",
#     collection_path="/tenders/{tender_id}/auction",
#     path="/tenders/{tender_id}/auction/{auction_lot_id}",
#     procurementMethodType="simple.defense",
#     description="Tender simple.defense auction data",
# )
class TenderSimpleDefenseAuctionResource(TenderUaAuctionResource):
    """ """
