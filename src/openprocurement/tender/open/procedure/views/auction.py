from cornice.resource import resource

from openprocurement.tender.core.procedure.views.auction import TenderAuctionResource
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD,
    ABOVE_THRESHOLD_EU,
    ABOVE_THRESHOLD_UA,
    ABOVE_THRESHOLD_UA_DEFENSE,
    BELOW_THRESHOLD,
    COMPETITIVE_ORDERING,
    OPEN_PROCUREMENT_METHOD_TYPES,
    OPEN_ROUTE_PREFIX,
    REQUEST_FOR_PROPOSAL,
    SIMPLE_DEFENSE,
)
from openprocurement.tender.open.procedure.state.tender import (
    AboveThresholdEUTenderState,
    AboveThresholdTenderState,
    AboveThresholdUATenderState,
    BelowThresholdTenderState,
    COTenderState,
    RFPTenderState,
    SimpleDefenseTenderState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Auction",
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    description="Tender auction data",
    procurementMethodType=OPEN_PROCUREMENT_METHOD_TYPES,
)
class OpenTenderAuctionResource(TenderAuctionResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdTenderState,
        ABOVE_THRESHOLD_UA: AboveThresholdUATenderState,
        ABOVE_THRESHOLD_EU: AboveThresholdEUTenderState,
        ABOVE_THRESHOLD_UA_DEFENSE: SimpleDefenseTenderState,
        SIMPLE_DEFENSE: SimpleDefenseTenderState,
        COMPETITIVE_ORDERING: COTenderState,
        BELOW_THRESHOLD: BelowThresholdTenderState,
        REQUEST_FOR_PROPOSAL: RFPTenderState,
    }
