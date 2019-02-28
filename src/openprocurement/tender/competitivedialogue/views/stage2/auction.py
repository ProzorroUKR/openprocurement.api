# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import (
    optendersresource,
)
from openprocurement.tender.openua.views.auction import TenderUaAuctionResource
from openprocurement.tender.openeu.views.auction import (
    TenderAuctionResource as TenderEUAuctionResource
)
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
)


@optendersresource(name='{}:Tender Auction'.format(STAGE_2_EU_TYPE),
                   collection_path='/tenders/{tender_id}/auction',
                   path='/tenders/{tender_id}/auction/{auction_lot_id}',
                   procurementMethodType=STAGE_2_EU_TYPE,
                   description="Competitive Dialogue Stage 2 EU auction data")
class CompetitiveDialogueStage2EUAuctionResource(TenderEUAuctionResource):
    """ Auctions resource """


@optendersresource(name='{}:Tender Auction'.format(STAGE_2_UA_TYPE),
                   collection_path='/tenders/{tender_id}/auction',
                   path='/tenders/{tender_id}/auction/{auction_lot_id}',
                   procurementMethodType=STAGE_2_UA_TYPE,
                   description="Competitive Dialogue Stage 2 UA auction data")
class CompetitiveDialogueStage2UAAuctionResource(TenderUaAuctionResource):
    """ Auctions resource """
