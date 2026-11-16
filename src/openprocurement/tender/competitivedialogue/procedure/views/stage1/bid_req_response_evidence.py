from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.state.bid_req_response_evidence import (
    CDBidReqResponseEvidenceState,
)
from openprocurement.tender.core.procedure.views.bid_req_response_evidence import (
    BidReqResponseEvidenceResource as BaseBidReqResponseEvidenceResource,
)


@resource(
    name="{}:Bid Requirement Response Evidence".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    description="Competitive Dialogue EU bidder evidences",
)
class CDEUBidReqResponseResource(BaseBidReqResponseEvidenceResource):
    state_class = CDBidReqResponseEvidenceState


@resource(
    name="{}:Bid Requirement Response Evidence".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    description="Competitive Dialogue EU bidder evidences",
)
class CDUABidReqResponseResource(BaseBidReqResponseEvidenceResource):
    state_class = CDBidReqResponseEvidenceState
