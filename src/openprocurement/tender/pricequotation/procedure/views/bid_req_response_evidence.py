from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.bid_req_response_evidence import (
    BidReqResponseEvidenceResource as BaseBidReqResponseEvidenceResource,
)
from openprocurement.tender.pricequotation.procedure.state.bid_req_response_evidence import (
    PQBidReqResponseEvidenceState,
)


@resource(
    name=f"{ProcurementMethodType.PRICE_QUOTATION}:Bid Requirement Response Evidence",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=ProcurementMethodType.PRICE_QUOTATION,
    description=f"{ProcurementMethodType.PRICE_QUOTATION} Tender UA bidder evidences",
)
class PQBidReqResponseResource(BaseBidReqResponseEvidenceResource):
    state_class = PQBidReqResponseEvidenceState
