# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.bid_document import TenderUaBidDocumentResource as TenderBidDocumentResource
from openprocurement.api.validation import (
    validate_file_update,
    validate_file_upload,
    validate_patch_document_data,
)
from openprocurement.tender.core.validation import (
    validate_bid_document_operation_period,
    unless_allowed_by_qualification_milestone,
    validate_bid_document_operation_in_award_status,
    validate_bid_document_in_tender_status,
)
from openprocurement.tender.openua.validation import validate_update_bid_document_confidentiality


@optendersresource(
    name="aboveThresholdUA.defense:Tender Bid Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender UA.defense bidder documents",
)
class TenderUaBidDocumentResource(TenderBidDocumentResource):

    @json_view(
        validators=(
            validate_file_upload,
            unless_allowed_by_qualification_milestone(
                validate_bid_document_in_tender_status
            ),
            validate_bid_document_operation_period,
            validate_bid_document_operation_in_award_status,
        ),
        permission="edit_bid",
    )
    def collection_post(self):
        return super(TenderUaBidDocumentResource, self).collection_post()

    @json_view(
        validators=(
            validate_file_update,
            unless_allowed_by_qualification_milestone(
                validate_bid_document_in_tender_status
            ),
            validate_bid_document_operation_period,
            validate_update_bid_document_confidentiality,
            validate_bid_document_operation_in_award_status,
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
                validate_bid_document_in_tender_status
            ),
            validate_bid_document_operation_period,
            validate_bid_document_operation_in_award_status,
            validate_update_bid_document_confidentiality,
        ),
        permission="edit_bid",
    )
    def patch(self):
        return super(TenderUaBidDocumentResource, self).patch()
