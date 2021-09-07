# -*- coding: utf-8 -*-
from openprocurement.tender.core.procedure.views.bid_document import TenderBidDocumentResource
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.models.document import PostDocument, PatchDocument, Document
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    validate_patch_data,
    validate_item_owner,
    validate_bid_document_operation_period,
    validate_upload_document,
    update_doc_fields_on_put_document,
    validate_data_model,
)
from openprocurement.tender.belowthreshold.procedure.validation import (
    validate_bid_document_operation_with_not_pending_award,
    validate_bid_document_operation_in_not_allowed_tender_status,
    validate_upload_documents_not_allowed_for_simple_pmr,
)
from cornice.resource import resource


@resource(
    name="belowThreshold:Tender Bid Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType="belowThreshold",
    description="Tender bidder documents",
)
class BelowThresholdTenderBidDocumentResource(TenderBidDocumentResource):

    @json_view(
        validators=(
            validate_item_owner("bid"),
            validate_input_data(PostDocument, allow_bulk=True),
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
            validate_item_owner("bid"),
            validate_input_data(PostDocument),
            validate_bid_document_operation_in_not_allowed_tender_status,
            validate_bid_document_operation_period,
            validate_bid_document_operation_with_not_pending_award,
            validate_upload_documents_not_allowed_for_simple_pmr,

            update_doc_fields_on_put_document,
            validate_upload_document,

            validate_data_model(Document),
        ),
        permission="edit_bid",
    )
    def put(self):
        return super(BelowThresholdTenderBidDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        validators=(
            validate_item_owner("bid"),
            validate_input_data(PatchDocument, none_means_remove=True),
            validate_patch_data(Document, item_name="document"),
            validate_bid_document_operation_in_not_allowed_tender_status,
            validate_bid_document_operation_period,
            validate_bid_document_operation_with_not_pending_award,
            validate_upload_documents_not_allowed_for_simple_pmr,
        ),
        permission="edit_bid",
    )
    def patch(self):
        return super(BelowThresholdTenderBidDocumentResource, self).patch()
