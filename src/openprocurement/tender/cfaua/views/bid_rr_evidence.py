# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.bid_rr_evidence import BaseBidRequirementResponseEvidenceResource
from openprocurement.tender.core.utils import optendersresource


@optendersresource(
    name="closeFrameworkAgreementUA:Bid Requirement Response Evidence",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender bidder evidences",
)
class BidRequirementResponseEvidenceResource(
    BaseBidRequirementResponseEvidenceResource
):
    pass
