# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.bid_rr_evidence import BaseBidRequirementResponseEvidenceResource
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE


@optendersresource(
    name="{}:Bid Requirement Response Evidence".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU bidder evidences",
)
class CDEUBidRequirementResponseEvidenceResource(
    BaseBidRequirementResponseEvidenceResource
):
    pass


@optendersresource(
    name="{}:Bid Requirement Response Evidence".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue EU bidder evidences",
)
class CDUABidRequirementResponseEvidenceResource(
    BaseBidRequirementResponseEvidenceResource
):
    pass
