from pyramid.security import Allow, Everyone

from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.state.tender_document import (
    TenderDocumentState,
)
from openprocurement.tender.core.procedure.validation import (
    get_tender_document_role,
)
from openprocurement.tender.core.procedure.views.document import (
    BaseDocumentResource,
    resolve_document,
)


class TenderDocumentResource(BaseDocumentResource):
    item_name = "tender"
    state_class = TenderDocumentState

    def __init__(self, request, context=None):
        super().__init__(request, context)  # resolve tender
        resolve_document(request, self.item_name, self.container)

    def allow_deletion(self):
        return True

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "upload_tender_documents"),
            (Allow, "g:bots", "upload_tender_documents"),
            (Allow, "g:auction", "upload_tender_documents"),
        ]
        return acl

    def set_doc_author(self, doc):
        doc["author"] = get_tender_document_role(self.request)
        return doc

    @json_view(permission="view_tender")
    def collection_get(self):
        return super().collection_get()

    @json_view(
        permission="view_tender",
    )
    def get(self):
        return super().get()

    @json_view(
        permission="upload_tender_documents",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        permission="upload_tender_documents",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        permission="upload_tender_documents",
    )
    def patch(self):
        return super().patch()

    @json_view(
        content_type="application/json",
        permission="upload_tender_documents",
    )
    def delete(self):
        self.state.validate_document_delete_request()
        return super().delete()
