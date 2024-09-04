from cornice.resource import resource

from openprocurement.api.procedure.validation import unless_item_owner
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.validation import validate_view_bids
from openprocurement.tender.core.procedure.views.bid_sign import BidSignResource
from openprocurement.tender.esco.procedure.serializers.bid import BidSerializer


@resource(
    name="esco:Tender Bid Sign",
    path="/tenders/{tender_id}/bids/{bid_id}/sign",
    description="Tender bid sign",
    procurementMethodType="esco",
)
class ESCOBidSignResource(BidSignResource):
    serializer_class = BidSerializer

    @json_view(
        permission="view_tender",
        validators=(
            unless_item_owner(
                validate_view_bids,
                item_name="bid",
            ),
        ),
    )
    def get(self):
        return super().get()
