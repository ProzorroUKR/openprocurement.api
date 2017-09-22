# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.auction import TenderUaAuctionResource as BaseResource


@optendersresource(name='aboveThresholdEU:Tender Auction',
                   collection_path='/tenders/{tender_id}/auction',
                   path='/tenders/{tender_id}/auction/{auction_lot_id}',
                   procurementMethodType='aboveThresholdEU',
                   description="Tender EU auction data")
class TenderAuctionResource(BaseResource):
    """ Auctions resouce """
