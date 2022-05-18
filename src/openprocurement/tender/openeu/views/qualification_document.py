# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
)
from openprocurement.api.validation import (
    validate_file_update,
    validate_patch_document_data,
    validate_file_upload,
)
from openprocurement.tender.core.views.document import CoreDocumentResource
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openeu.validation import (
    validate_qualification_document_operation_not_in_pending,
    validate_qualification_document_operation_not_in_allowed_status,
    validate_qualification_update_with_cancellation_lot_pending,
)


# @qualifications_resource(
#     name="aboveThresholdEU:Tender Qualification Documents",
#     collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/documents",
#     path="/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}",
#     procurementMethodType="aboveThresholdEU",
#     description="Tender qualification documents",
# )
class TenderQualificationDocumentResource(CoreDocumentResource):
    container = "documents"
    context_name = "tender_qualification"

    def set_doc_author(self, doc):
        doc.author = self.request.authenticated_role
        return doc

    @json_view(
        permission="upload_qualification_documents",
        validators=(
            validate_file_upload,
            validate_qualification_update_with_cancellation_lot_pending,
            validate_qualification_document_operation_not_in_allowed_status,
            validate_qualification_document_operation_not_in_pending,
        ),
    )
    def collection_post(self):
        """Tender Qualification Document Upload
        """
        return super(TenderQualificationDocumentResource, self).collection_post()

    @json_view(
        validators=(
            validate_file_update,
            validate_qualification_update_with_cancellation_lot_pending,
            validate_qualification_document_operation_not_in_allowed_status,
            validate_qualification_document_operation_not_in_pending,
        ),
        permission="upload_qualification_documents",
    )
    def put(self):
        """Tender Qualification Document Update"""
        return super(TenderQualificationDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_document_data,
            validate_qualification_update_with_cancellation_lot_pending,
            validate_qualification_document_operation_not_in_allowed_status,
            validate_qualification_document_operation_not_in_pending,
        ),
        permission="upload_qualification_documents",
    )
    def patch(self):
        """Tender Qualification Document Update"""
        return super(TenderQualificationDocumentResource, self).patch()
