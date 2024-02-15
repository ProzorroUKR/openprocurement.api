from cornice.resource import resource

from openprocurement.tender.core.procedure.views.bid_req_response import (
    BidReqResponseResource as BaseBidReqResponseResource,
)
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD_GROUP,
    ABOVE_THRESHOLD_GROUP_NAME,
)


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Bid Requirement Response",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    description="Tender bidder requirement responses",
)
class BidReqResponseResource(BaseBidReqResponseResource):
    pass
