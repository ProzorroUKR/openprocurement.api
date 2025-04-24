from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.competitiveordering.procedure.state.tender import (
    OpenTenderState,
)
from openprocurement.tender.core.procedure.views.auction import (
    TenderAuctionResource as BaseTenderAuctionResource,
)


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Auction",
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tender auction data",
)
class TenderAuctionResource(BaseTenderAuctionResource):
    state_class = OpenTenderState
