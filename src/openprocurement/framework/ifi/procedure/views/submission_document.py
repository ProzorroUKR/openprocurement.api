from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    update_doc_fields_on_put_document,
    validate_data_model,
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
    validate_upload_document,
)
from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.models.submission_document import (
    PatchSubmissionDocument,
    PostSubmissionDocument,
    SubmissionDocument,
)
from openprocurement.framework.core.procedure.validation import (
    validate_document_operation_in_not_allowed_period,
    validate_download_submission_document,
)
from openprocurement.framework.core.procedure.views.document import (
    CoreSubmissionDocumentResource,
)
from openprocurement.framework.ifi.constants import IFI_TYPE


@resource(
    name=f"{IFI_TYPE}:Submission Documents",
    collection_path="/submissions/{submission_id}/documents",
    path="/submissions/{submission_id}/documents/{document_id}",
    description="Submission related binary files (PDFs, etc.)",
    submissionType=IFI_TYPE,
)
class SubmissionDocumentResource(CoreSubmissionDocumentResource):
    @json_view(
        permission="view_framework",
    )
    def collection_get(self):
        return super().collection_get()

    @json_view(
        validators=(validate_download_submission_document,),
        permission="view_framework",
    )
    def get(self):
        return super().get()

    @json_view(
        validators=(
            validate_item_owner("submission"),
            validate_input_data(PostSubmissionDocument, allow_bulk=True),
            validate_document_operation_in_not_allowed_period,
        ),
        permission="edit_submission",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        validators=(
            validate_item_owner("submission"),
            validate_input_data(PostSubmissionDocument),
            update_doc_fields_on_put_document,
            validate_upload_document,
            validate_data_model(SubmissionDocument),
            validate_document_operation_in_not_allowed_period,
        ),
        permission="edit_submission",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        validators=(
            validate_item_owner("submission"),
            validate_input_data(PatchSubmissionDocument, none_means_remove=True),
            validate_patch_data_simple(SubmissionDocument, item_name="document"),
            validate_document_operation_in_not_allowed_period,
        ),
        permission="edit_submission",
    )
    def patch(self):
        return super().patch()
