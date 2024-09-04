from cornice.resource import resource

from openprocurement.tender.core.procedure.views.bid_sign import BidSignResource
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD_GROUP,
    ABOVE_THRESHOLD_GROUP_NAME,
)


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Tender Bid Sign",
    path="/tenders/{tender_id}/bids/{bid_id}/sign",
    description="Tender bid sign",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
)
class UABidSignResource(BidSignResource):
    pass
