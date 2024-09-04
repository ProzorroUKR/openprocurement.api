from cornice.resource import resource

from openprocurement.tender.core.procedure.views.bid_sign import BidSignResource


@resource(
    name="belowThreshold:Tender Bid Sign",
    path="/tenders/{tender_id}/bids/{bid_id}/sign",
    description="Tender bid sign",
    procurementMethodType="belowThreshold",
)
class BelowThresholdBidSignResource(BidSignResource):
    pass
