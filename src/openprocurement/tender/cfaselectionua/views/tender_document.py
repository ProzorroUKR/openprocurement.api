# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
)

from openprocurement.tender.belowthreshold.views.tender_document import (
    TenderDocumentResource,
)
from openprocurement.api.validation import (
    validate_file_update,
    validate_patch_document_data,
    validate_file_upload,
)
from openprocurement.tender.core.utils import save_tender, optendersresource, apply_patch
from openprocurement.tender.core.validation import validate_tender_document_update_not_by_author_or_tender_owner
from openprocurement.tender.cfaselectionua.validation import validate_document_operation_in_not_allowed_tender_status


# @optendersresource(
#     name="closeFrameworkAgreementSelectionUA:Tender Documents",
#     collection_path="/tenders/{tender_id}/documents",
#     path="/tenders/{tender_id}/documents/{document_id}",
#     procurementMethodType="closeFrameworkAgreementSelectionUA",
#     description="Tender related binary files (PDFs, etc.)",
# )
class TenderDocumentResource(TenderDocumentResource):

    @json_view(
        permission="upload_tender_documents",
        validators=(validate_file_upload, validate_document_operation_in_not_allowed_tender_status),
    )
    def collection_post(self):
        """Tender Document Upload"""
        return super(TenderDocumentResource, self).collection_post()

    @json_view(
        permission="upload_tender_documents",
        validators=(
            validate_file_update,
            validate_document_operation_in_not_allowed_tender_status,
            validate_tender_document_update_not_by_author_or_tender_owner,
        ),
    )
    def put(self):
        """Tender Document Update"""
        return super(TenderDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        permission="upload_tender_documents",
        validators=(
            validate_patch_document_data,
            validate_document_operation_in_not_allowed_tender_status,
            validate_tender_document_update_not_by_author_or_tender_owner,
        ),
    )
    def patch(self):
        """Tender Document Update"""
        return super(TenderDocumentResource, self).patch()
