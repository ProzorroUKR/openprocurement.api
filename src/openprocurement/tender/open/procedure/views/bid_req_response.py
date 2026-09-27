from cornice.resource import resource

from openprocurement.tender.core.procedure.views.bid_req_response import BidReqResponseResource
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD,
    ABOVE_THRESHOLD_EU,
    ABOVE_THRESHOLD_UA,
    BELOW_THRESHOLD,
    COMPETITIVE_ORDERING,
    OPEN_ROUTE_PREFIX,
    REQUEST_FOR_PROPOSAL,
    SIMPLE_DEFENSE,
)
from openprocurement.tender.open.procedure.state.bid_req_response import (
    AboveThresholdBidReqResponseState,
    AboveThresholdEUBidReqResponseState,
    AboveThresholdUABidReqResponseState,
    BelowThresholdBidReqResponseState,
    COBidReqResponseState,
    RFPBidReqResponseState,
    SimpleDefenseBidReqResponseState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Bid Requirement Response",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}",
    description="Tender bidder requirement responses",
    procurementMethodType=[
        ABOVE_THRESHOLD,
        ABOVE_THRESHOLD_UA,
        ABOVE_THRESHOLD_EU,
        SIMPLE_DEFENSE,
        COMPETITIVE_ORDERING,
        BELOW_THRESHOLD,
        REQUEST_FOR_PROPOSAL,
    ],
)
class OpenBidReqResponseResource(BidReqResponseResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdBidReqResponseState,
        ABOVE_THRESHOLD_UA: AboveThresholdUABidReqResponseState,
        ABOVE_THRESHOLD_EU: AboveThresholdEUBidReqResponseState,
        SIMPLE_DEFENSE: SimpleDefenseBidReqResponseState,
        COMPETITIVE_ORDERING: COBidReqResponseState,
        BELOW_THRESHOLD: BelowThresholdBidReqResponseState,
        REQUEST_FOR_PROPOSAL: RFPBidReqResponseState,
    }
