from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.validation import validate_view_bid_document
from openprocurement.tender.core.procedure.views.bid import resolve_bid
from openprocurement.tender.core.procedure.views.document import BaseDocumentResource, resolve_document
from pyramid.security import Allow, Everyone, ALL_PERMISSIONS


class TenderBidDocumentResource(BaseDocumentResource):
    item_name = "bid"

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_bid"),
            (Allow, "g:brokers", "edit_bid"),
            (Allow, "g:Administrator", "edit_bid"),  # wtf ???
            (Allow, "g:admins", ALL_PERMISSIONS),    # some tests use this, idk why
        ]
        return acl

    def get_modified(self):
        return self.request.validated["tender"]["status"] != "active.tendering"

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_bid(request)
            resolve_document(request, self.item_name, self.container)

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
