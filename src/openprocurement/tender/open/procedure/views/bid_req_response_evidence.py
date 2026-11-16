from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.bid_req_response_evidence import BidReqResponseEvidenceResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX
from openprocurement.tender.open.procedure.state.bid_req_response_evidence import (
    AboveThresholdBidReqResponseEvidenceState,
    AboveThresholdEUBidReqResponseEvidenceState,
    AboveThresholdUABidReqResponseEvidenceState,
    BelowThresholdBidReqResponseEvidenceState,
    COBidReqResponseEvidenceState,
    OpenTenderingBidReqResponseEvidenceState,
    RFPBidReqResponseEvidenceState,
    SimpleDefenseBidReqResponseEvidenceState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Bid Requirement Response Evidence",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    description="Tender UA bidder evidences",
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
class OpenBidReqResponseEvidenceResource(BidReqResponseEvidenceResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdBidReqResponseEvidenceState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUABidReqResponseEvidenceState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdEUBidReqResponseEvidenceState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingBidReqResponseEvidenceState,
        ProcurementMethodType.SIMPLE_DEFENSE: SimpleDefenseBidReqResponseEvidenceState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COBidReqResponseEvidenceState,
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdBidReqResponseEvidenceState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPBidReqResponseEvidenceState,
    }
