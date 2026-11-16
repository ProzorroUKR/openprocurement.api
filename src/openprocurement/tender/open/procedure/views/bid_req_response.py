from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.bid_req_response import BidReqResponseResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX
from openprocurement.tender.open.procedure.state.bid_req_response import (
    AboveThresholdBidReqResponseState,
    AboveThresholdEUBidReqResponseState,
    AboveThresholdUABidReqResponseState,
    BelowThresholdBidReqResponseState,
    COBidReqResponseState,
    OpenTenderingBidReqResponseState,
    RFPBidReqResponseState,
    SimpleDefenseBidReqResponseState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Bid Requirement Response",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}",
    description="Tender bidder requirement responses",
    procurementMethodType=[
        ProcurementMethodType.ABOVE_THRESHOLD,
        ProcurementMethodType.ABOVE_THRESHOLD_UA,
        ProcurementMethodType.ABOVE_THRESHOLD_EU,
        ProcurementMethodType.OPEN_TENDERING,
        ProcurementMethodType.SIMPLE_DEFENSE,
        ProcurementMethodType.COMPETITIVE_ORDERING,
        ProcurementMethodType.BELOW_THRESHOLD,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL,
    ],
)
class OpenBidReqResponseResource(BidReqResponseResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdBidReqResponseState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUABidReqResponseState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdEUBidReqResponseState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingBidReqResponseState,
        ProcurementMethodType.SIMPLE_DEFENSE: SimpleDefenseBidReqResponseState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COBidReqResponseState,
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdBidReqResponseState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPBidReqResponseState,
    }
