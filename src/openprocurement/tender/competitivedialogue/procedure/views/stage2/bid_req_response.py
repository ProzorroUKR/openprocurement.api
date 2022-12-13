from cornice.resource import resource

from openprocurement.tender.core.procedure.views.bid_req_response import (
    BidReqResponseResource as BaseBidReqResponseResource,
)
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE


@resource(
    name="{}:Bid Requirement Response".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU bidder requirement responses",
)
class CDEUBidReqResponseResource(BaseBidReqResponseResource):
    pass


@resource(
    name="{}:Bid Requirement Response".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage 2 UA bidder requirement responses",
)
class CDUABidReqResponseResource(BaseBidReqResponseResource):
    pass
