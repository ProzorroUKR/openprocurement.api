from cornice.resource import resource

from openprocurement.tender.core.procedure.views.bid_req_response_evidence import BidReqResponseEvidenceResource
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
from openprocurement.tender.open.procedure.state.bid_req_response_evidence import (
    AboveThresholdBidReqResponseEvidenceState,
    AboveThresholdEUBidReqResponseEvidenceState,
    AboveThresholdUABidReqResponseEvidenceState,
    BelowThresholdBidReqResponseEvidenceState,
    COBidReqResponseEvidenceState,
    RFPBidReqResponseEvidenceState,
    SimpleDefenseBidReqResponseEvidenceState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Bid Requirement Response Evidence",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    description="Tender UA bidder evidences",
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
class OpenBidReqResponseEvidenceResource(BidReqResponseEvidenceResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdBidReqResponseEvidenceState,
        ABOVE_THRESHOLD_UA: AboveThresholdUABidReqResponseEvidenceState,
        ABOVE_THRESHOLD_EU: AboveThresholdEUBidReqResponseEvidenceState,
        SIMPLE_DEFENSE: SimpleDefenseBidReqResponseEvidenceState,
        COMPETITIVE_ORDERING: COBidReqResponseEvidenceState,
        BELOW_THRESHOLD: BelowThresholdBidReqResponseEvidenceState,
        REQUEST_FOR_PROPOSAL: RFPBidReqResponseEvidenceState,
    }
