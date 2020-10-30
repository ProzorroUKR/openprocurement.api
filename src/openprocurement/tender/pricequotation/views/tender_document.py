# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.api.validation import validate_patch_document_data,\
    validate_file_upload, validate_file_update
from openprocurement.tender.belowthreshold.views.tender_document import\
    TenderDocumentResource
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.pricequotation.constants import PMT
from openprocurement.tender.core.validation import (
    validate_tender_document_update_not_by_author_or_tender_owner,
    validate_patch_document_contract_proforma,
)
from openprocurement.tender.pricequotation.validation import validate_document_operation_in_not_allowed_period


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
            validate_document_operation_in_not_allowed_period
        ),
    )
    def collection_post(self):
        return super(PQTenderDocumentResource, self).collection_post()

    @json_view(
        permission="upload_tender_documents",
        validators=(
            validate_file_update,
            validate_document_operation_in_not_allowed_period,
            validate_tender_document_update_not_by_author_or_tender_owner
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
            validate_patch_document_contract_proforma,
            validate_document_operation_in_not_allowed_period,
            validate_tender_document_update_not_by_author_or_tender_owner
        ),
    )
    def patch(self):
        """Tender Document Update"""
        return super(PQTenderDocumentResource, self).patch()
