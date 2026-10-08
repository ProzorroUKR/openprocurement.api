from cornice.resource import resource

from openprocurement.tender.cfaselectionua.procedure.state.bid_req_response import (
    CFASelectionBidReqResponseState,
)
from openprocurement.tender.core.procedure.views.bid_req_response import (
    BidReqResponseResource as BaseBidReqResponseResource,
)


@resource(
    name="closeFrameworkAgreementSelectionUA:Bid Requirement Response",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender bidder requirement responses",
)
class BidReqResponseResource(BaseBidReqResponseResource):
    state_class = CFASelectionBidReqResponseState
