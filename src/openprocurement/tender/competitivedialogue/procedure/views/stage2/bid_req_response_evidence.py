from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.state.stage2.bid_req_response_evidence import (
    CDStage2EUBidReqResponseEvidenceState,
    CDStage2UABidReqResponseEvidenceState,
)
from openprocurement.tender.core.procedure.views.bid_req_response_evidence import (
    BidReqResponseEvidenceResource as BaseBidReqResponseEvidenceResource,
)


@resource(
    name="{}:Bid Requirement Response Evidence".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    description="Competitive Dialogue Stage 2 EU bidder evidences",
)
class CDEUBidReqResponseResource(BaseBidReqResponseEvidenceResource):
    state_class = CDStage2EUBidReqResponseEvidenceState


@resource(
    name="{}:Bid Requirement Response Evidence".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    description="Competitive Dialogue Stage 2 EU bidder evidences",
)
class CDUABidReqResponseResource(BaseBidReqResponseEvidenceResource):
    state_class = CDStage2UABidReqResponseEvidenceState
