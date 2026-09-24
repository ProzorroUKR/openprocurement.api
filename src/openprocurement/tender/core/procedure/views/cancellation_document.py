from pyramid.security import ALL_PERMISSIONS, Allow, Everyone

from openprocurement.api.procedure.validation import (
    validate_request_by_state,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.state.cancellation_document import (
    CancellationDocumentState,
)
from openprocurement.tender.core.procedure.views.cancellation import (
    resolve_cancellation,
)
from openprocurement.tender.core.procedure.views.document import (
    BaseDocumentResource,
    resolve_document,
)


class CancellationDocumentResource(BaseDocumentResource):
    state_class = CancellationDocumentState
    item_name = "cancellation"

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "upload_cancellation_documents"),
            (Allow, "g:admins", ALL_PERMISSIONS),
        ]
        return acl

    def __init__(self, request, context=None):
        super().__init__(request, context)  # resolve tender
        resolve_cancellation(request)
        resolve_document(request, self.item_name, self.container)

    @json_view(
        validators=(validate_request_by_state,),
        permission="upload_cancellation_documents",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        validators=(validate_request_by_state,),
        permission="upload_cancellation_documents",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        validators=(validate_request_by_state,),
        permission="upload_cancellation_documents",
    )
    def patch(self):
        return super().patch()
