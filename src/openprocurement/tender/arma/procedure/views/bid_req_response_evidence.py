from cornice.resource import resource

from openprocurement.tender.arma.constants import (
    ARMA_PROCUREMENT_METHOD_TYPES,
    ARMA_ROUTE_PREFIX,
    COMPLEX_ASSET_ARMA,
    SIMPLE_ASSET_ARMA,
)
from openprocurement.tender.arma.procedure.state.bid_req_response_evidence import (
    ComplexAssetBidReqResponseEvidenceState,
    SimpleAssetBidReqResponseEvidenceState,
)
from openprocurement.tender.core.procedure.views.bid_req_response_evidence import (
    BidReqResponseEvidenceResource as BaseBidReqResponseEvidenceResource,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Bid Requirement Response Evidence",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    description="Tender bidder evidences",
)
class BidReqResponseEvidenceResource(BaseBidReqResponseEvidenceResource):
    state_classes = {
        COMPLEX_ASSET_ARMA: ComplexAssetBidReqResponseEvidenceState,
        SIMPLE_ASSET_ARMA: SimpleAssetBidReqResponseEvidenceState,
    }
