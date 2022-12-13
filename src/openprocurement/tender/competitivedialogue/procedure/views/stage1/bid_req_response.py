from cornice.resource import resource

from openprocurement.tender.core.procedure.views.bid_req_response import (
    BidReqResponseResource as BaseBidReqResponseResource,
)
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE


@resource(
    name="{}:Bid Requirement Response".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU bidder requirement responses",
)
class CDEUBidReqResponseResource(BaseBidReqResponseResource):
    pass


@resource(
    name="{}:Bid Requirement Response".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA bidder requirement responses",
)
class CDUABidReqResponseResource(BaseBidReqResponseResource):
    pass
