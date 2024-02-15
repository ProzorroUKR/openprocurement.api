from cornice.resource import resource

from openprocurement.tender.core.procedure.views.auction import TenderAuctionResource
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD_GROUP,
    ABOVE_THRESHOLD_GROUP_NAME,
)
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Tender Auction",
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    description="Tender auction data",
)
class TenderAuctionResource(TenderAuctionResource):
    state_class = OpenTenderState
