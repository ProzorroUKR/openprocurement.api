from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.models.document import PostDocument, PatchDocument, Document
from openprocurement.framework.core.procedure.validation import (
    validate_framework_owner,
    validate_document_operation_in_not_allowed_status,
)
from openprocurement.framework.core.procedure.views.document import CoreQualificationDocumentResource
from openprocurement.framework.electroniccatalogue.constants import ELECTRONIC_CATALOGUE_TYPE
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    validate_patch_data_simple,
    validate_data_model,
    validate_upload_document,
    update_doc_fields_on_put_document,
)


@resource(
    name=f"{ELECTRONIC_CATALOGUE_TYPE}:Qualification Documents",
    collection_path="/qualifications/{qualification_id}/documents",
    path="/qualifications/{qualification_id}/documents/{document_id}",
    description="Qualification related binary files (PDFs, etc.)",
    qualificationType=ELECTRONIC_CATALOGUE_TYPE,
)
class QualificationDocumentResource(CoreQualificationDocumentResource):
    @json_view(permission="view_framework")
    def collection_get(self):
        return super().collection_get()

    @json_view(permission="view_framework")
    def get(self):
        return super().get()

    @json_view(
        validators=(
                validate_framework_owner("qualification"),
                validate_document_operation_in_not_allowed_status,
                validate_input_data(PostDocument, allow_bulk=True),
        ),
        permission="edit_qualification",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        validators=(
                validate_framework_owner("qualification"),
                validate_document_operation_in_not_allowed_status,
                validate_input_data(PostDocument),
                update_doc_fields_on_put_document,
                validate_upload_document,
                validate_data_model(Document),
        ),
        permission="edit_qualification",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        validators=(
                validate_framework_owner("qualification"),
                validate_document_operation_in_not_allowed_status,
                validate_input_data(PatchDocument, none_means_remove=True),
                validate_patch_data_simple(Document, item_name="document"),
        ),
        permission="edit_qualification",
    )
    def patch(self):
        return super().patch()
