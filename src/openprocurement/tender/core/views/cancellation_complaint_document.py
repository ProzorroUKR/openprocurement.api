# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
)
from openprocurement.api.validation import (
    validate_file_update,
    validate_patch_document_data,
    validate_file_upload,
)
from openprocurement.tender.core.validation import (
    validate_complaint_document_update_not_by_author,
)
from openprocurement.tender.core.views.document import CoreDocumentResource


class BaseTenderComplaintCancellationDocumentResource(CoreDocumentResource):
    container = "documents"
    context_name = "tender_cancellation_complaint"

    def set_doc_author(self, doc):
        doc.author = self.request.authenticated_role
        return doc

    @json_view(
        validators=(
            validate_file_upload,
        ),
        permission="edit_complaint",
    )
    def collection_post(self):
        """Tender Cancellation Complaint Document Upload
        """
        return super(BaseTenderComplaintCancellationDocumentResource, self).collection_post()

    @json_view(
        validators=(
            validate_file_update,
            validate_complaint_document_update_not_by_author,
        ),
        permission="edit_complaint",
    )
    def put(self):
        """Tender Cancellation Complaint Document Update"""
        return super(BaseTenderComplaintCancellationDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_document_data,
            validate_complaint_document_update_not_by_author,
        ),
        permission="edit_complaint",
    )
    def patch(self):
        """Tender Cancellation Complaint Document Update"""
        return super(BaseTenderComplaintCancellationDocumentResource, self).patch()
