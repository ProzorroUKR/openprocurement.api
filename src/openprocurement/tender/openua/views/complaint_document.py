# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.api.validation import (
    validate_file_update,
    validate_patch_document_data,
    validate_file_upload,
)
from openprocurement.tender.core.validation import (
    validate_complaint_document_update_not_by_author,
    validate_status_and_role_for_complaint_document_operation,
)
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.complaint_document import TenderComplaintDocumentResource
from openprocurement.tender.openua.validation import validate_complaint_document_operation_not_in_allowed_status


@optendersresource(
    name="aboveThresholdUA:Tender Complaint Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender complaint documents",
)
class TenderUaComplaintDocumentResource(TenderComplaintDocumentResource):
    @json_view(
        validators=(
            validate_file_upload,
            validate_complaint_document_operation_not_in_allowed_status,
            validate_status_and_role_for_complaint_document_operation,
        ),
        permission="edit_complaint",
    )
    def collection_post(self):
        """Tender Complaint Document Upload
        """
        return super(TenderUaComplaintDocumentResource, self).collection_post()

    @json_view(
        validators=(
            validate_file_update,
            validate_complaint_document_update_not_by_author,
            validate_complaint_document_operation_not_in_allowed_status,
            validate_status_and_role_for_complaint_document_operation,
        ),
        permission="edit_complaint",
    )
    def put(self):
        """Tender Complaint Document Update"""
        return super(TenderUaComplaintDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_document_data,
            validate_complaint_document_update_not_by_author,
            validate_complaint_document_operation_not_in_allowed_status,
            validate_status_and_role_for_complaint_document_operation,
        ),
        permission="edit_complaint",
    )
    def patch(self):
        """Tender Complaint Document Update"""
        return super(TenderUaComplaintDocumentResource, self).patch()
