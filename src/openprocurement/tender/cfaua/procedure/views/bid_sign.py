from cornice.resource import resource

from openprocurement.api.procedure.validation import unless_item_owner
from openprocurement.api.utils import json_view
from openprocurement.tender.cfaua.procedure.serializers.bid import BidSerializer
from openprocurement.tender.core.procedure.validation import (
    validate_bid_operation_in_tendering,
)
from openprocurement.tender.core.procedure.views.bid_sign import BidSignResource


@resource(
    name="closeFrameworkAgreementUA:Tender Bid Sign",
    path="/tenders/{tender_id}/bids/{bid_id}/sign",
    description="Tender bid sign",
    procurementMethodType="closeFrameworkAgreementUA",
)
class CFAUABidSignResource(BidSignResource):
    serializer_class = BidSerializer

    @json_view(
        permission="view_tender",
        validators=(
            unless_item_owner(
                validate_bid_operation_in_tendering,
                item_name="bid",
            ),
        ),
    )
    def get(self):
        return super().get()
