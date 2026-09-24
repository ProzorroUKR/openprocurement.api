from pyramid.security import Allow, Everyone

from openprocurement.api.procedure.validation import (
    validate_request_by_state,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.state.complaint_appeal_document import (
    ComplaintAppealDocumentState,
)
from openprocurement.tender.core.procedure.views.complaint import resolve_complaint
from openprocurement.tender.core.procedure.views.complaint_appeal import (
    resolve_complaint_appeal,
)
from openprocurement.tender.core.procedure.views.document import (
    BaseDocumentResource,
    resolve_document,
)


class BaseComplaintAppealDocumentResource(BaseDocumentResource):
    item_name = "appeal"
    state_class = ComplaintAppealDocumentState

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "upload_complaint_appeal_documents"),
        ]
        return acl

    def set_doc_author(self, doc):
        doc["author"] = self.request.authenticated_role
        return doc

    @json_view(permission="view_tender")
    def collection_get(self):
        return super().collection_get()

    @json_view(
        validators=(validate_request_by_state,),
        permission="view_tender",
    )
    def get(self):
        return super().get()

    @json_view(
        validators=(validate_request_by_state,),
        permission="upload_complaint_appeal_documents",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        validators=(validate_request_by_state,),
        permission="upload_complaint_appeal_documents",
    )
    def put(self):
        return super().put()

    @json_view(
        validators=(validate_request_by_state,),
        permission="upload_complaint_appeal_documents",
    )
    def patch(self):
        return super().patch()


class BaseTenderComplaintAppealDocumentResource(BaseComplaintAppealDocumentResource):
    def __init__(self, request, context=None):
        super().__init__(request, context)  # resolve tender
        resolve_complaint(request)
        resolve_complaint_appeal(request)
        resolve_document(request, self.item_name, self.container)
