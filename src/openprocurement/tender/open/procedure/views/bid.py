from cornice.resource import resource

from openprocurement.tender.core.procedure.views.bid import TenderBidResource
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
from openprocurement.tender.open.procedure.state.bid import (
    AboveThresholdBidState,
    AboveThresholdEUBidState,
    AboveThresholdUABidState,
    BelowThresholdBidState,
    COBidState,
    DefenseBidState,
    RFPBidState,
    SimpleDefenseBidState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    description="Tender bids",
    procurementMethodType=OPEN_PROCUREMENT_METHOD_TYPES,
)
class OpenTenderBidResource(TenderBidResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdBidState,
        ABOVE_THRESHOLD_UA: AboveThresholdUABidState,
        ABOVE_THRESHOLD_EU: AboveThresholdEUBidState,
        ABOVE_THRESHOLD_UA_DEFENSE: DefenseBidState,
        SIMPLE_DEFENSE: SimpleDefenseBidState,
        COMPETITIVE_ORDERING: COBidState,
        BELOW_THRESHOLD: BelowThresholdBidState,
        REQUEST_FOR_PROPOSAL: RFPBidState,
    }
