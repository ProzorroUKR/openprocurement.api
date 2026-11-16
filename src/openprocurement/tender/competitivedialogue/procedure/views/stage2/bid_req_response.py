from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.state.stage2.bid_req_response import (
    CDStage2EUBidReqResponseState,
    CDStage2UABidReqResponseState,
)
from openprocurement.tender.core.procedure.views.bid_req_response import (
    BidReqResponseResource as BaseBidReqResponseResource,
)


@resource(
    name="{}:Bid Requirement Response".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    description="Competitive Dialogue Stage 2 EU bidder requirement responses",
)
class CDEUBidReqResponseResource(BaseBidReqResponseResource):
    state_class = CDStage2EUBidReqResponseState


@resource(
    name="{}:Bid Requirement Response".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    description="Competitive Dialogue Stage 2 UA bidder requirement responses",
)
class CDUABidReqResponseResource(BaseBidReqResponseResource):
    state_class = CDStage2UABidReqResponseState
