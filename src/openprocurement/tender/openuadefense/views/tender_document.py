# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.api.validation import validate_file_upload, validate_file_update, validate_patch_document_data
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.validation import (
    validate_document_operation_in_not_allowed_period,
    validate_tender_document_update_not_by_author_or_tender_owner,
    validate_patch_document_contract_proforma,
)
from openprocurement.tender.openua.views.tender_document import TenderUaDocumentResource as TenderDocumentResource
from openprocurement.tender.openuadefense.validation import validate_update_tender


@optendersresource(
    name="aboveThresholdUA.defense:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender UA.defense related binary files (PDFs, etc.)",
)
class TenderUaDocumentResource(TenderDocumentResource):
    @json_view(
        permission="upload_tender_documents",
        validators=(
            validate_file_upload,
            validate_document_operation_in_not_allowed_period,
            validate_update_tender,
        ),
    )
    def collection_post(self):
        return super(TenderUaDocumentResource, self).collection_post()

    @json_view(
        permission="upload_tender_documents",
        validators=(
            validate_file_update,
            validate_document_operation_in_not_allowed_period,
            validate_tender_document_update_not_by_author_or_tender_owner,
            validate_update_tender,
        ),
    )
    def put(self):
        return super(TenderUaDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        permission="upload_tender_documents",
        validators=(
            validate_patch_document_data,
            validate_patch_document_contract_proforma,
            validate_document_operation_in_not_allowed_period,
            validate_tender_document_update_not_by_author_or_tender_owner,
            validate_update_tender,
        ),
    )
    def patch(self):
        return super(TenderUaDocumentResource, self).patch()
