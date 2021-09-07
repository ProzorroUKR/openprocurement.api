from openprocurement.tender.core.procedure.views.bid_document import TenderBidDocumentResource
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.models.document import PostDocument, PatchDocument, Document
from openprocurement.tender.cfaselectionua.procedure.validation import (
    validate_bid_document_operation_with_not_pending_award,
    validate_bid_document_operation_in_not_allowed_tender_status,
)
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    validate_patch_data,
    validate_view_bid_document,
    validate_item_owner,
    validate_bid_document_operation_period,
    validate_upload_document,
    update_doc_fields_on_put_document,
    validate_data_model,
)
from cornice.resource import resource


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Bid Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender bidder documents",
)
class TenderCFASUABidDocumentResource(TenderBidDocumentResource):
    @json_view(
        validators=(
            validate_view_bid_document,
        ),
        permission="view_tender",
    )
    def get(self):
        return super().get()

    @json_view(
        validators=(
            validate_item_owner("bid"),
            validate_input_data(PostDocument, allow_bulk=True),

            validate_bid_document_operation_in_not_allowed_tender_status,
            validate_bid_document_operation_with_not_pending_award,
            validate_bid_document_operation_period,
        ),
        permission="edit_bid",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        validators=(
            validate_item_owner("bid"),
            validate_input_data(PostDocument),

            validate_bid_document_operation_in_not_allowed_tender_status,
            validate_bid_document_operation_with_not_pending_award,
            validate_bid_document_operation_period,

            update_doc_fields_on_put_document,
            validate_upload_document,
            validate_data_model(Document),
        ),
        permission="edit_bid",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        validators=(
            validate_item_owner("bid"),

            validate_input_data(PatchDocument, none_means_remove=True),
            validate_patch_data(Document, item_name="document"),

            validate_bid_document_operation_in_not_allowed_tender_status,
            validate_bid_document_operation_with_not_pending_award,
            validate_bid_document_operation_period,
        ),
        permission="edit_bid",
    )
    def patch(self):
        return super().patch()
