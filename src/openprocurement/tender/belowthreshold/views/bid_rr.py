# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.bid_rr import BaseBidRequirementResponseResource
from openprocurement.tender.core.utils import optendersresource


@optendersresource(
    name="belowThreshold:Bid Requirement Response",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType="belowThreshold",
    description="Tender bidder requirement responses",
)
class BidRequirementResponseResource(BaseBidRequirementResponseResource):
    pass
