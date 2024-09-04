from cornice.resource import resource

from openprocurement.tender.core.procedure.views.bid_sign import BidSignResource


@resource(
    name="simple.defense:Tender Bid Sign",
    path="/tenders/{tender_id}/bids/{bid_id}/sign",
    description="Tender bid sign",
    procurementMethodType="simple.defense",
)
class SimpleDefenseBidSignResource(BidSignResource):
    pass
