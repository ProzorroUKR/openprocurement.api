from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.validation import validate_view_bid_document
from openprocurement.tender.core.procedure.views.bid import TenderBidResource
from openprocurement.tender.core.procedure.views.document import BaseDocumentResource


class TenderBidDocumentResource(BaseDocumentResource, TenderBidResource):
    item_name = "bid"

    def __init__(self, request, context=None):
        TenderBidResource.__init__(self, request, context)
        BaseDocumentResource.__init__(self, request, context)

    @json_view(
        validators=(
            validate_view_bid_document,
        ),
        permission="view_tender",
    )
    def collection_get(self):
        return super().collection_get()

    @json_view(permission="view_tender", validators=(validate_view_bid_document,))
    def get(self):
        return super().get()
