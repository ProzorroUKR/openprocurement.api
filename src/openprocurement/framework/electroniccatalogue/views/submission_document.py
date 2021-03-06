# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
)
from openprocurement.api.validation import (
    validate_file_update,
    validate_patch_document_data,
    validate_file_upload,
)
from openprocurement.framework.core.utils import submissionsresource
from openprocurement.framework.core.validation import (
    validate_document_operation_in_not_allowed_period
)
from openprocurement.framework.core.views.document import CoreSubmissionDocumentResource


@submissionsresource(
    name="electronicCatalogue:Submission Documents",
    collection_path="/submissions/{submission_id}/documents",
    path="/submissions/{submission_id}/documents/{document_id}",
    description="Submission related binary files (PDFs, etc.)",
)
class SubmissionDocumentResource(CoreSubmissionDocumentResource):
    context_name = "submission"

    @json_view(permission="view_submission")
    def collection_get(self):
        """Submission Documents List"""
        return super(SubmissionDocumentResource, self).collection_get()

    @json_view(
        permission="edit_submission",
        validators=(
            validate_document_operation_in_not_allowed_period,
            validate_file_upload,
        ),
    )
    def collection_post(self):
        """Submission Document Upload"""
        return super(SubmissionDocumentResource, self).collection_post()

    @json_view(permission="view_submission")
    def get(self):
        """Submission Document Read"""
        return super(SubmissionDocumentResource, self).get()

    @json_view(
        permission="edit_submission",
        validators=(
            validate_document_operation_in_not_allowed_period,
            validate_file_update,
        ),
    )
    def put(self):
        """Submission Document Update"""
        return super(SubmissionDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        permission="edit_submission",
        validators=(
            validate_document_operation_in_not_allowed_period,
            validate_patch_document_data,
        ),
    )
    def patch(self):
        """Submission Document Update"""
        return super(SubmissionDocumentResource, self).patch()
