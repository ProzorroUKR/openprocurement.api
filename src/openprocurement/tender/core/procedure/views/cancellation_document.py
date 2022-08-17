from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.views.cancellation import resolve_cancellation
from openprocurement.tender.core.procedure.views.document import BaseDocumentResource, resolve_document
from openprocurement.tender.core.procedure.state.cancellation_document import CancellationDocumentState
from openprocurement.tender.core.procedure.models.document import PostDocument, PatchDocument, Document
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    validate_patch_data,
    validate_item_owner,
    unless_admins,
    update_doc_fields_on_put_document,
    validate_upload_document,
    validate_data_model,
)
from pyramid.security import Allow, Everyone, ALL_PERMISSIONS


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
        validators=(
            unless_admins(validate_item_owner("tender")),
            validate_input_data(PostDocument, allow_bulk=True),
        ),
        permission="upload_cancellation_documents",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        validators=(
            unless_admins(validate_item_owner("tender")),
            validate_input_data(PostDocument),

            update_doc_fields_on_put_document,
            validate_upload_document,
            validate_data_model(Document),
        ),
        permission="upload_cancellation_documents",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        validators=(
            unless_admins(validate_item_owner("tender")),
            validate_input_data(PatchDocument, none_means_remove=True),
            validate_patch_data(Document, item_name="document"),
        ),
        permission="upload_cancellation_documents",
    )
    def patch(self):
        return super().patch()
