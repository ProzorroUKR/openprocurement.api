# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.api.validation import validate_patch_document_data,\
    validate_file_upload, validate_file_update
from openprocurement.tender.belowthreshold.views.tender_document import\
    TenderDocumentResource
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.pricequotation.constants import PMT


@optendersresource(
    name="{}:Tender Documents".format(PMT),
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=PMT,
    description="Tender related binary files (PDFs, etc.)",
)
class PQTenderDocumentResource(TenderDocumentResource):

    @json_view(
        permission="upload_tender_documents",
        validators=(
            validate_file_upload,
            # validate_operation_with_document_not_in_active_status
        ),
    )
    def collection_post(self):
        return super(PQTenderDocumentResource, self).collection_post()

    @json_view(
        permission="upload_tender_documents",
        validators=(
            validate_file_update,
            # validate_operation_with_document_not_in_active_status
        ),
    )
    def put(self):
        """Tender Document Update"""
        return super(PQTenderDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        permission="upload_tender_documents",
        validators=(
            validate_patch_document_data,
            # validate_operation_with_document_not_in_active_status
        ),
    )
    def patch(self):
        """Tender Document Update"""
        return super(PQTenderDocumentResource, self).patch()
