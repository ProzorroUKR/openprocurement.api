from cornice.resource import resource

from openprocurement.tender.core.procedure.views.bid_req_response_evidence import (
    BidReqResponseEvidenceResource as BaseBidReqResponseEvidenceResource,
)
from openprocurement.tender.esco.procedure.state.bid_req_response_evidence import (
    ESCOBidReqResponseEvidenceState,
)


@resource(
    name="esco:Bid Requirement Response Evidence",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType="esco",
    description="Tender UA bidder evidences",
)
class BidReqResponseResource(BaseBidReqResponseEvidenceResource):
    state_class = ESCOBidReqResponseEvidenceState
