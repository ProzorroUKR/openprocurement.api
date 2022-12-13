# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.bid_rr_evidence import BaseBidRequirementResponseEvidenceResource
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.open.constants import ABOVE_THRESHOLD


# @optendersresource(
#     name=f"{ABOVE_THRESHOLD}:Bid Requirement Response Evidence",
#     collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences",
#     path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
#     procurementMethodType=ABOVE_THRESHOLD,
#     description="Tender bidder evidences",
# )
# class BidRequirementResponseEvidenceResource(
#     BaseBidRequirementResponseEvidenceResource
# ):
#     pass
