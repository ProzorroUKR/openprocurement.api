from openprocurement.api.utils import (
    json_view,
)
from openprocurement.tender.core.utils import (
    optendersresource,
)
from openprocurement.api.validation import (
    validate_file_update,
    validate_patch_document_data,
    validate_file_upload,
)
from openprocurement.tender.core.validation import (
    validate_document_operation_in_not_allowed_period,
    validate_tender_document_update_not_by_author_or_tender_owner,
)
from openprocurement.tender.belowthreshold.views.tender_document import TenderDocumentResource
from openprocurement.tender.openua.validation import validate_update_tender_document


# @optendersresource(
#     name="aboveThresholdUA:Tender Documents",
#     collection_path="/tenders/{tender_id}/documents",
#     path="/tenders/{tender_id}/documents/{document_id}",
#     procurementMethodType="aboveThresholdUA",
#     description="Tender UA related binary files (PDFs, etc.)",
# )
class TenderUaDocumentResource(TenderDocumentResource):
    def pre_save(self):
        tender = self.request.validated["tender"]
        status = self.request.validated["tender_status"]
        if self.request.authenticated_role == "tender_owner" and status == "active.tendering":
            tender.invalidate_bids_data()

    @json_view(
        permission="upload_tender_documents",
        validators=(
            validate_file_upload,
            validate_document_operation_in_not_allowed_period,
            validate_update_tender_document,
        ),
    )
    def collection_post(self):
        """Tender Document Upload"""
        return super(TenderUaDocumentResource, self).collection_post()

    @json_view(
        permission="upload_tender_documents",
        validators=(
                validate_file_update,
                validate_document_operation_in_not_allowed_period,
                validate_tender_document_update_not_by_author_or_tender_owner,
                validate_update_tender_document,
        ),
    )
    def put(self):
        """Tender Document Update"""
        return super(TenderUaDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        permission="upload_tender_documents",
        validators=(
                validate_patch_document_data,
                validate_document_operation_in_not_allowed_period,
                validate_tender_document_update_not_by_author_or_tender_owner,
                validate_update_tender_document,
        ),
    )
    def patch(self):
        """Tender Document Update"""
        return super(TenderUaDocumentResource, self).patch()
