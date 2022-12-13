from cornice.resource import resource

from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.core.procedure.views.bid_req_response_evidence import (
    BidReqResponseEvidenceResource as BaseBidReqResponseEvidenceResource,
)


@resource(
    name=f"{ABOVE_THRESHOLD}:Bid Requirement Response Evidence",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    description="Tender UA bidder evidences",
)
class BidReqResponseResource(BaseBidReqResponseEvidenceResource):
    pass
