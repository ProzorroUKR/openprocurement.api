from cornice.resource import resource

from openprocurement.tender.core.procedure.views.bid_sign import BidSignResource
from openprocurement.tender.pricequotation.constants import PQ


@resource(
    name=f"{PQ}:Tender Bid Sign",
    path="/tenders/{tender_id}/bids/{bid_id}/sign",
    description="Tender bid sign",
    procurementMethodType=PQ,
)
class PQBidSignResource(BidSignResource):
    pass
