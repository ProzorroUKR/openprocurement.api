from pyramid.security import ALL_PERMISSIONS, Allow, Everyone

from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.state.bid_document import (
    BidDocumentState,
    BidFinancialDocumentState,
)
from openprocurement.tender.core.procedure.views.bid import resolve_bid
from openprocurement.tender.core.procedure.views.document import (
    BaseDocumentResource,
    resolve_document,
)


class BaseTenderBidDocumentResource(BaseDocumentResource):
    item_name = "bid"
    state_class = BidDocumentState
    container = "documents"

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_bid"),
            (Allow, "g:brokers", "edit_bid"),
            (Allow, "g:Administrator", "edit_bid"),  # wtf ???
            (Allow, "g:admins", ALL_PERMISSIONS),  # some tests use this, idk why
        ]
        return acl

    def get_modified(self):
        return self.request.validated["tender"]["status"] != "active.tendering"

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_bid(request)
            resolve_document(request, self.item_name, self.container)

    def validate(self, document):
        self.state.validate_sign_documents_already_exists(document, self.container)

    @json_view(
        permission="view_tender",
    )
    def get(self):
        return super().get()

    @json_view(
        permission="view_tender",
    )
    def collection_get(self):
        self.state.validate_document_get_request()
        return super().collection_get()

    @json_view(
        permission="edit_bid",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        permission="edit_bid",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        permission="edit_bid",
    )
    def patch(self):
        return super().patch()

    @json_view(
        content_type="application/json",
        permission="edit_bid",
    )
    def delete(self):
        self.state.validate_document_delete_request()
        return super().delete()


class BaseTenderBidEligibilityDocumentResource(BaseTenderBidDocumentResource):
    """Tender Bid Eligibility Documents"""

    container = "eligibilityDocuments"


class BaseTenderBidFinancialDocumentResource(BaseTenderBidDocumentResource):
    """Tender Bid Financial Documents"""

    container = "financialDocuments"
    state_class = BidFinancialDocumentState


class BaseTenderBidQualificationDocumentResource(BaseTenderBidDocumentResource):
    """Tender Bid Qualification Documents"""

    container = "qualificationDocuments"
    state_class = BidFinancialDocumentState
