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
    validate_status_and_role_for_complaint_document_operation,
    validate_award_complaint_document_operation_only_for_active_lots,
    validate_award_complaint_document_operation_not_in_allowed_status,
)

from openprocurement.tender.core.utils import optendersresource

from openprocurement.tender.belowthreshold.validation import validate_role_and_status_for_add_complaint_document
from openprocurement.tender.core.views.document import CoreDocumentResource


@optendersresource(
    name="belowThreshold:Tender Award Complaint Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="belowThreshold",
    description="Tender award complaint documents",
)
class TenderAwardComplaintDocumentResource(CoreDocumentResource):
    container = "documents"
    context_name = "tender_award_complaint"

    def set_doc_author(self, doc):
        doc.author = self.request.authenticated_role
        return doc

    @json_view(
        permission="edit_complaint",
        validators=(
            validate_file_upload,
            validate_award_complaint_document_operation_not_in_allowed_status,
            validate_award_complaint_document_operation_only_for_active_lots,
            validate_role_and_status_for_add_complaint_document,
        ),
    )
    def collection_post(self):
        """Tender Award Complaint Document Upload
        """
        return super(TenderAwardComplaintDocumentResource, self).collection_post()

    @json_view(
        validators=(
            validate_file_update,
            validate_complaint_document_update_not_by_author,
            validate_award_complaint_document_operation_not_in_allowed_status,
            validate_award_complaint_document_operation_only_for_active_lots,
            validate_status_and_role_for_complaint_document_operation,
        ),
        permission="edit_complaint",
    )
    def put(self):
        """Tender Award Complaint Document Update"""
        return super(TenderAwardComplaintDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_document_data,
            validate_complaint_document_update_not_by_author,
            validate_award_complaint_document_operation_not_in_allowed_status,
            validate_award_complaint_document_operation_only_for_active_lots,
            validate_status_and_role_for_complaint_document_operation,
        ),
        permission="edit_complaint",
    )
    def patch(self):
        """Tender Award Complaint Document Update"""
        return super(TenderAwardComplaintDocumentResource, self).patch()
