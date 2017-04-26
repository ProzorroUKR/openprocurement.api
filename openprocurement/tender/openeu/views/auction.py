# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    context_unpack
)
from openprocurement.tender.core.utils import (
    optendersresource,
    apply_patch,
    save_tender
)
from openprocurement.tender.core.validation import validate_tender_auction_data
from openprocurement.tender.openua.views.auction import TenderUaAuctionResource as BaseResource
from openprocurement.tender.openua.utils import add_next_award


@optendersresource(name='aboveThresholdEU:Tender Auction',
                   collection_path='/tenders/{tender_id}/auction',
                   path='/tenders/{tender_id}/auction/{auction_lot_id}',
                   procurementMethodType='aboveThresholdEU',
                   description="Tender EU auction data")
class TenderAuctionResource(BaseResource):
    """ Auctions resouce """
