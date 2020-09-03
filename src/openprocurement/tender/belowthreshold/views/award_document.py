# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.api.validation import validate_file_update, validate_file_upload, validate_patch_document_data
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.document import BaseDocumentResource
from openprocurement.tender.core.validation import (
    validate_award_document_tender_not_in_allowed_status_base,
    validate_award_document_lot_not_in_allowed_status,
    validate_award_document_author,
)


@optendersresource(
    name="belowThreshold:Tender Award Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType="belowThreshold",
    description="Tender award documents",
)
class TenderAwardDocumentResource(BaseDocumentResource):
    context_name = "tender_award"

    @json_view(permission="view_tender")
    def collection_get(self):
        return super(TenderAwardDocumentResource, self).collection_get()

    @json_view(
        validators=(
            validate_file_upload,
            validate_award_document_tender_not_in_allowed_status_base,
            validate_award_document_lot_not_in_allowed_status,
            validate_award_document_author
        ),
        permission="upload_tender_documents")
    def collection_post(self):
        return super(TenderAwardDocumentResource, self).collection_post()

    @json_view(permission="view_tender")
    def get(self):
        return super(TenderAwardDocumentResource, self).get()

    @json_view(
        validators=(
            validate_file_update,
            validate_award_document_tender_not_in_allowed_status_base,
            validate_award_document_lot_not_in_allowed_status,
            validate_award_document_author
        ),
        permission="edit_tender")
    def put(self):
        return super(TenderAwardDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_document_data,
            validate_award_document_tender_not_in_allowed_status_base,
            validate_award_document_lot_not_in_allowed_status,
            validate_award_document_author
        ),
        permission="edit_tender",
    )
    def patch(self):
        return super(TenderAwardDocumentResource, self).patch()
