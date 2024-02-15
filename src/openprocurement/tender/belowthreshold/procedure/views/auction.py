from cornice.resource import resource

from openprocurement.tender.belowthreshold.procedure.state.tender import (
    BelowThresholdTenderState,
)
from openprocurement.tender.core.procedure.views.auction import TenderAuctionResource


@resource(
    name="belowThreshold:Tender Auction",
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType="belowThreshold",
    description="Tender auction data",
)
class TenderAuctionResource(TenderAuctionResource):
    state_class = BelowThresholdTenderState
