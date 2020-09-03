# -*- coding: utf-8 -*-
from openprocurement.api.utils import raise_operation_error, error_handler, json_view
from openprocurement.api.validation import validate_file_update, validate_file_upload, validate_patch_document_data
from openprocurement.tender.belowthreshold.views.award_document import TenderAwardDocumentResource
from openprocurement.tender.core.validation import (
    validate_award_document_tender_not_in_allowed_status_base,
    validate_award_document_lot_not_in_allowed_status,
    validate_award_document_author,
)
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.validation import validate_accepted_complaints


@optendersresource(
    name="aboveThresholdUA:Tender Award Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender award documents",
)
class TenderUaAwardDocumentResource(TenderAwardDocumentResource):
    @json_view(
        validators=(
            validate_file_upload,
            validate_award_document_tender_not_in_allowed_status_base,
            validate_award_document_lot_not_in_allowed_status,
            validate_award_document_author,
            validate_accepted_complaints
        ),
        permission="upload_tender_documents",
    )
    def collection_post(self):
        return super(TenderUaAwardDocumentResource, self).collection_post()

    @json_view(
        validators=(
            validate_file_update,
            validate_award_document_tender_not_in_allowed_status_base,
            validate_award_document_lot_not_in_allowed_status,
            validate_award_document_author,
            validate_accepted_complaints
        ),
        permission="edit_tender",
    )
    def put(self):
        return super(TenderUaAwardDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_document_data,
            validate_award_document_tender_not_in_allowed_status_base,
            validate_award_document_lot_not_in_allowed_status,
            validate_award_document_author,
            validate_accepted_complaints
        ),
        permission="edit_tender",
    )
    def patch(self):
        return super(TenderUaAwardDocumentResource, self).patch()
