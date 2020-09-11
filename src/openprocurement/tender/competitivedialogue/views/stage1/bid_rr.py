# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.bid_rr import BaseBidRequirementResponseResource
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE


@optendersresource(
    name="{}:Bid Requirement Response".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU bidder requirement responses",
)
class CDEUBidRequirementResponseResource(BaseBidRequirementResponseResource):
    pass


@optendersresource(
    name="{}:Bid Requirement Response".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA bidder requirement responses",
)
class CDUABidRequirementResponseResource(BaseBidRequirementResponseResource):
    pass
