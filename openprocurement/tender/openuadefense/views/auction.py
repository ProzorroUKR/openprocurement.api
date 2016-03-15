# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.auction import TenderUaAuctionResource as TenderAuctionResource


@opresource(name='Tender UA.defense Auction',
            collection_path='/tenders/{tender_id}/auction',
            path='/tenders/{tender_id}/auction/{auction_lot_id}',
            procurementMethodType='aboveThresholdUA.defense',
            description="Tender UA.defense auction data")
class TenderUaAuctionResource(TenderAuctionResource):
    """ """
