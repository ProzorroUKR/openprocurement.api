from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.competitivedialogue.procedure.state.bid_req_response import (
    CDBidReqResponseState,
)
from openprocurement.tender.core.procedure.views.bid_req_response import (
    BidReqResponseResource as BaseBidReqResponseResource,
)


@resource(
    name="{}:Bid Requirement Response".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU bidder requirement responses",
)
class CDEUBidReqResponseResource(BaseBidReqResponseResource):
    state_class = CDBidReqResponseState


@resource(
    name="{}:Bid Requirement Response".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA bidder requirement responses",
)
class CDUABidReqResponseResource(BaseBidReqResponseResource):
    state_class = CDBidReqResponseState
