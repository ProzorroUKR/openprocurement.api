# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.auction import TenderUaAuctionResource as BaseResource

LOGGER = getLogger(__name__)


@opresource(name='Tender EU Auction',
            collection_path='/tenders/{tender_id}/auction',
            path='/tenders/{tender_id}/auction/{auction_lot_id}',
            procurementMethodType='aboveThresholdEU',
            description="Tender EU auction data")
class TenderAuctionResource(BaseResource):
    """ Auctions resouce """
