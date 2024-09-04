from openprocurement.api.procedure.validation import unless_item_owner
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.serializers.bid import BidSerializer
from openprocurement.tender.core.procedure.validation import validate_view_bids
from openprocurement.tender.core.procedure.views.bid import resolve_bid
from openprocurement.tender.core.procedure.views.sign import BaseSignResource


class BidSignResource(BaseSignResource):
    serializer_class = BidSerializer
    obj_name = "bid"

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_bid(request)

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
