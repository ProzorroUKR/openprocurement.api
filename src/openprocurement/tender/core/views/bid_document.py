# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
)
from openprocurement.api.validation import (
    validate_file_update,
    validate_patch_document_data,
    validate_file_upload,
)
from openprocurement.tender.core.validation import (
    validate_bid_document_operation_period,
    validate_view_bid_document,
    validate_bid_document_operation_with_not_pending_award,
    validate_bid_document_operation_in_not_allowed_tender_status,
)
from openprocurement.tender.core.views.document import CoreDocumentResource


class TenderBidDocumentResource(CoreDocumentResource):
    container = "documents"
    context_name = "tender_bid"

    def pre_save(self):
        if self.request.validated["tender_status"] == "active.tendering":
            self.request.validated["tender"].modified = False

    def get_doc_view_role(self, doc):
        return "view"

    @json_view(
        validators=(
            validate_view_bid_document,
        ),
        permission="view_tender",
    )
    def collection_get(self):
        """Tender Bid Documents List"""
        return super(TenderBidDocumentResource, self).collection_get()

    @json_view(
        validators=(
            validate_file_upload,
            validate_bid_document_operation_in_not_allowed_tender_status,
            validate_bid_document_operation_period,
            validate_bid_document_operation_with_not_pending_award,
        ),
        permission="edit_bid",
    )
    def collection_post(self):
        """Tender Bid Document Upload
        """
        return super(TenderBidDocumentResource, self).collection_post()

    @json_view(permission="view_tender", validators=(validate_view_bid_document,))
    def get(self):
        """Tender Bid Document Read"""
        return super(TenderBidDocumentResource, self).get()

    @json_view(
        validators=(
            validate_file_update,
            validate_bid_document_operation_in_not_allowed_tender_status,
            validate_bid_document_operation_period,
            validate_bid_document_operation_with_not_pending_award,
        ),
        permission="edit_bid",
    )
    def put(self):
        """Tender Bid Document Update"""
        return super(TenderBidDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_document_data,
            validate_bid_document_operation_in_not_allowed_tender_status,
            validate_bid_document_operation_period,
            validate_bid_document_operation_with_not_pending_award,
        ),
        permission="edit_bid",
    )
    def patch(self):
        """Tender Bid Document Update"""
        return super(TenderBidDocumentResource, self).patch()
