# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.bid_document import TenderBidDocumentResource
from openprocurement.tender.core.utils import optendersresource
from openprocurement.api.utils import json_view
from openprocurement.api.validation import (
    validate_file_upload, 
    validate_file_update, 
    validate_patch_document_data,
)
from openprocurement.tender.belowthreshold.validation import validate_upload_documents_not_allowed_for_simple_pmr
from openprocurement.tender.core.validation import (
    validate_bid_document_operation_period,
    validate_bid_document_operation_with_not_pending_award,
    validate_bid_document_operation_in_not_allowed_tender_status,
)


# @optendersresource(
#     name="belowThreshold:Tender Bid Documents",
#     collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
#     path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
#     procurementMethodType="belowThreshold",
#     description="Tender bidder documents",
# )
class BelowThresholdTenderBidDocumentResource(TenderBidDocumentResource):
    pass

    @json_view(
        validators=(
            validate_file_upload,
            validate_bid_document_operation_in_not_allowed_tender_status,
            validate_bid_document_operation_period,
            validate_bid_document_operation_with_not_pending_award,
            validate_upload_documents_not_allowed_for_simple_pmr,
        ),
        permission="edit_bid",
    )
    def collection_post(self):
        return super(BelowThresholdTenderBidDocumentResource, self).collection_post()

    @json_view(
        validators=(
                validate_file_update,
                validate_bid_document_operation_in_not_allowed_tender_status,
                validate_bid_document_operation_period,
                validate_bid_document_operation_with_not_pending_award,
                validate_upload_documents_not_allowed_for_simple_pmr,
        ),
        permission="edit_bid",
    )
    def put(self):
        return super(BelowThresholdTenderBidDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        validators=(
                validate_patch_document_data,
                validate_bid_document_operation_in_not_allowed_tender_status,
                validate_bid_document_operation_period,
                validate_bid_document_operation_with_not_pending_award,
                validate_upload_documents_not_allowed_for_simple_pmr,
        ),
        permission="edit_bid",
    )
    def patch(self):
        return super(BelowThresholdTenderBidDocumentResource, self).patch()
