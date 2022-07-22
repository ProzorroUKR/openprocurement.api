from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.views.document import BaseDocumentResource, resolve_document
from openprocurement.tender.core.procedure.state.tender_document import TenderDocumentState
from openprocurement.tender.core.procedure.validation import get_tender_document_role
from pyramid.security import Allow, Everyone


class TenderDocumentResource(BaseDocumentResource):
    item_name = "tender"
    state_class = TenderDocumentState

    def __init__(self, request, context=None):
        super().__init__(request, context)  # resolve tender
        resolve_document(request, self.item_name, self.container)

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

    @json_view(permission="view_tender")
    def get(self):
        return super().get()
