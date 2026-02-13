from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.bid_req_response import (
    BidReqResponseResource as BaseBidReqResponseResource,
)


@resource(
    name="complexAsset.arma:Bid Requirement Response",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses",
    path="/tenders/{tender_id}/bids/{bid_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender bidder requirement responses",
)
class BidReqResponseResource(BaseBidReqResponseResource):
    pass
