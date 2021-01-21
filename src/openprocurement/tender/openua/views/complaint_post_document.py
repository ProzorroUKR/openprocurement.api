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

from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.document import CoreDocumentResource
from openprocurement.tender.openua.validation import (
    validate_complaint_post_review_date,
    validate_complaint_post_complaint_status,
    validate_complaint_post_document_upload_by_author,
)


@optendersresource(
    name="aboveThresholdUA:Tender Complaint Post Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender complaint post documents",
)
class TenderComplaintPostDocumentResource(CoreDocumentResource):
    context_name = "tender_complaint_post"

    def set_doc_author(self, doc):
        doc.author = self.request.authenticated_role
        return doc

    @json_view(
        validators=(
            validate_file_upload,
            validate_complaint_post_document_upload_by_author,
            validate_complaint_post_complaint_status,
            validate_complaint_post_review_date,
        ),
        permission="edit_complaint",
    )
    def collection_post(self):
        """
        Tender Complaint Post Document Upload
        """
        return super(TenderComplaintPostDocumentResource, self).collection_post()

    @json_view(
        validators=(
            validate_file_update,
            validate_complaint_document_update_not_by_author,
            validate_complaint_post_complaint_status,
            validate_complaint_post_review_date,
        ),
        permission="edit_complaint",
    )
    def put(self):
        """
        Tender Complaint Post Document Update
        """
        return super(TenderComplaintPostDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_document_data,
            validate_complaint_document_update_not_by_author,
            validate_complaint_post_complaint_status,
            validate_complaint_post_review_date,
        ),
        permission="edit_complaint",
    )
    def patch(self):
        """
        Tender Complaint Post Document Update
        """
        return super(TenderComplaintPostDocumentResource, self).patch()
