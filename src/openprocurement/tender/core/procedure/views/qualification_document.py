from pyramid.security import Allow, Everyone

from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.state.qualification_document import (
    QualificationDocumentState,
)
from openprocurement.tender.core.procedure.validation import (
    get_qualification_document_role,
)
from openprocurement.tender.core.procedure.views.document import (
    BaseDocumentResource,
    resolve_document,
)
from openprocurement.tender.core.procedure.views.qualification import (
    resolve_qualification,
)


class BaseQualificationDocumentResource(BaseDocumentResource):
    item_name = "qualification"
    state_class = QualificationDocumentState

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:bots", "upload_qualification_documents"),
            (Allow, "g:bots", "edit_qualification_documents"),
            (Allow, "g:brokers", "upload_qualification_documents"),
            (Allow, "g:brokers", "edit_qualification_documents"),
            (Allow, "g:admins", "upload_qualification_documents"),
            (Allow, "g:admins", "edit_qualification_documents"),
        ]
        return acl

    def __init__(self, request, context=None):
        super().__init__(request, context)
        resolve_qualification(request)
        resolve_document(request, self.item_name, self.container)

    def set_doc_author(self, doc):
        doc["author"] = get_qualification_document_role(self.request)
        return doc

    @json_view(
        permission="upload_qualification_documents",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        permission="edit_qualification_documents",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        permission="edit_qualification_documents",
    )
    def patch(self):
        return super().patch()
