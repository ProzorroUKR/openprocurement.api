from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.views.document import BaseDocumentResource, resolve_document
from openprocurement.tender.core.procedure.views.qualification import resolve_qualification
from openprocurement.tender.core.procedure.validation import get_qualification_document_role
from openprocurement.tender.core.procedure.models.document import PostDocument, PatchDocument, Document
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    validate_patch_data,
    validate_item_owner,
    unless_bots,
    update_doc_fields_on_put_document,
    validate_upload_document,
    validate_data_model,
    validate_qualification_update_with_cancellation_lot_pending,
    validate_qualification_document_operation_not_in_allowed_status,
    validate_qualification_document_operation_not_in_pending,
)
from pyramid.security import Allow, Everyone


class BaseQualificationDocumentResource(BaseDocumentResource):
    item_name = "qualification"

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
        validators=(
            unless_bots(validate_item_owner("tender")),
            validate_input_data(PostDocument, allow_bulk=True),

            validate_qualification_update_with_cancellation_lot_pending,
            validate_qualification_document_operation_not_in_allowed_status,
            validate_qualification_document_operation_not_in_pending,
        ),
        permission="upload_qualification_documents",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        validators=(
            unless_bots(validate_item_owner("tender")),
            validate_input_data(PostDocument),

            validate_qualification_update_with_cancellation_lot_pending,
            validate_qualification_document_operation_not_in_allowed_status,
            validate_qualification_document_operation_not_in_pending,

            update_doc_fields_on_put_document,
            validate_upload_document,
            validate_data_model(Document),
        ),
        permission="edit_qualification_documents",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        validators=(
            unless_bots(validate_item_owner("tender")),
            validate_input_data(PatchDocument, none_means_remove=True),
            validate_patch_data(Document, item_name="document"),

            validate_qualification_update_with_cancellation_lot_pending,
            validate_qualification_document_operation_not_in_allowed_status,
            validate_qualification_document_operation_not_in_pending,
        ),
        permission="edit_qualification_documents",
    )
    def patch(self):
        return super().patch()
