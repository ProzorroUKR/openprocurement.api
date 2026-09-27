from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.competitivedialogue.procedure.state.bid_req_response_evidence import (
    CDBidReqResponseEvidenceState,
)
from openprocurement.tender.core.procedure.views.bid_req_response_evidence import (
    BidReqResponseEvidenceResource as BaseBidReqResponseEvidenceResource,
)


@resource(
    name="{}:Bid Requirement Response Evidence".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU bidder evidences",
)
class CDEUBidReqResponseResource(BaseBidReqResponseEvidenceResource):
    state_class = CDBidReqResponseEvidenceState


@resource(
    name="{}:Bid Requirement Response Evidence".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue EU bidder evidences",
)
class CDUABidReqResponseResource(BaseBidReqResponseEvidenceResource):
    state_class = CDBidReqResponseEvidenceState
