# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.auction import TenderAuctionResource as TenderEUAuctionResource


@opresource(name='Tender ESCO EU Auction',
            collection_path='/tenders/{tender_id}/auction',
            path='/tenders/{tender_id}/auction/{auction_lot_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU Auction data")
class TenderESCOEUAuctionResource(TenderEUAuctionResource):
    """ Tender ESCO EU Auction Resource """
