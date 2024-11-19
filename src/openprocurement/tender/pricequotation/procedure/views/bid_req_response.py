from cornice.resource import resource

from openprocurement.tender.core.procedure.views.bid_req_response import (
    BidReqResponseResource as BaseBidReqResponseResource,
)
from openprocurement.tender.pricequotation.constants import PQ


@resource(
    name=f"{PQ}:Bid Requirement Response",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=PQ,
    description=f"{PQ} Tender UA bidder requirement responses",
)
class PQBidReqResponseResource(BaseBidReqResponseResource):
    pass
