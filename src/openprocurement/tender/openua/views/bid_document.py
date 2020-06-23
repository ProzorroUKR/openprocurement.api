# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.api.validation import validate_file_update, validate_file_upload, validate_patch_document_data
from openprocurement.api.auth import extract_access_token
from openprocurement.tender.core.validation import (
    validate_view_bid_document,
    validate_bid_document_in_tender_status,
    validate_bid_document_operation_period,
    unless_allowed_by_qualification_milestone,
)
from openprocurement.tender.core.views.bid_document import TenderBidDocumentResource
from openprocurement.tender.openua.validation import (
    validate_download_bid_document,
    validate_bid_document_operation_in_award_status,
    validate_update_bid_document_confidentiality,
)
from openprocurement.tender.core.utils import optendersresource


@optendersresource(
    name="aboveThresholdUA:Tender Bid Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender UA bidder documents",
)
class TenderUaBidDocumentResource(TenderBidDocumentResource):

    def _get_doc_view_role(self, doc):
        return doc.view_role()

    @json_view(
        validators=(
            validate_view_bid_document,
            validate_download_bid_document,
        ),
        permission="view_tender",
    )
    def get(self):
        return super(TenderUaBidDocumentResource, self).get()

    @json_view(
        validators=(
            validate_file_upload,
            unless_allowed_by_qualification_milestone(
                validate_bid_document_in_tender_status,
                validate_bid_document_operation_in_award_status,
            ),
            validate_bid_document_operation_period,
        ),
        permission="edit_bid",
    )
    def collection_post(self):
        return super(TenderUaBidDocumentResource, self).collection_post()

    @json_view(
        validators=(
            validate_file_update,
            unless_allowed_by_qualification_milestone(
                validate_bid_document_in_tender_status,
                validate_bid_document_operation_in_award_status,
            ),
            validate_bid_document_operation_period,
            validate_update_bid_document_confidentiality,
        ),
        permission="edit_bid",
    )
    def put(self):
        return super(TenderUaBidDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_document_data,
            unless_allowed_by_qualification_milestone(
                validate_bid_document_in_tender_status,
                validate_bid_document_operation_in_award_status,
            ),
            validate_bid_document_operation_period,
            validate_update_bid_document_confidentiality,
        ),
        permission="edit_bid",
    )
    def patch(self):
        return super(TenderUaBidDocumentResource, self).patch()
