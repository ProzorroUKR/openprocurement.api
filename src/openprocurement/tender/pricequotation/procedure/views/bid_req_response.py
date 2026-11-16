from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.bid_req_response import (
    BidReqResponseResource as BaseBidReqResponseResource,
)
from openprocurement.tender.pricequotation.procedure.state.bid_req_response import (
    PQBidReqResponseState,
)


@resource(
    name=f"{ProcurementMethodType.PRICE_QUOTATION}:Bid Requirement Response",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=ProcurementMethodType.PRICE_QUOTATION,
    description=f"{ProcurementMethodType.PRICE_QUOTATION} Tender UA bidder requirement responses",
)
class PQBidReqResponseResource(BaseBidReqResponseResource):
    state_class = PQBidReqResponseState
