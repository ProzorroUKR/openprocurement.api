# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.auction import TenderAuctionResource as TenderEUAuctionResource


@optendersresource(name='esco.EU:Tender Auction',
                   collection_path='/tenders/{tender_id}/auction',
                   path='/tenders/{tender_id}/auction/{auction_lot_id}',
                   procurementMethodType='esco.EU',
                   description="Tender ESCO EU Auction data")
class TenderESCOEUAuctionResource(TenderEUAuctionResource):
    """ Tender ESCO EU Auction Resource """
