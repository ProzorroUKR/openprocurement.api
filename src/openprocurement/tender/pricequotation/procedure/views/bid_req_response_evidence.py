from cornice.resource import resource

from openprocurement.tender.core.procedure.views.bid_req_response_evidence import (
    BidReqResponseEvidenceResource as BaseBidReqResponseEvidenceResource,
)
from openprocurement.tender.pricequotation.constants import PQ


@resource(
    name=f"{PQ}:Bid Requirement Response Evidence",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=PQ,
    description=f"{PQ} Tender UA bidder evidences",
)
class PQBidReqResponseResource(BaseBidReqResponseEvidenceResource):
    pass
