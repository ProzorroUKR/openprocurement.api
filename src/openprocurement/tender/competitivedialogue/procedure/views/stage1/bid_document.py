from openprocurement.tender.openeu.procedure.views.bid_document import OpenEUTenderBidDocumentResource
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.api.utils import json_view
from openprocurement.tender.competitivedialogue.procedure.models.document import PostDocument, PatchDocument, Document
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    validate_patch_data,
    validate_item_owner,
    validate_bid_document_operation_period,
    unless_allowed_by_qualification_milestone,
    validate_upload_document,
    update_doc_fields_on_put_document,
    validate_data_model,
)
from openprocurement.tender.openua.procedure.validation import (
    validate_bid_document_in_tender_status,
    validate_bid_document_operation_in_award_status,
    validate_update_bid_document_confidentiality,
)
from openprocurement.tender.openeu.procedure.validation import (
    validate_bid_document_operation_in_bid_status,
)
from cornice.resource import resource


@resource(
    name="{}:Tender Bid Documents".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU bidder documents",
)
class EUTenderBidDocumentResource(OpenEUTenderBidDocumentResource):
    @json_view(
        validators=(
            validate_item_owner("bid"),
            validate_input_data(PostDocument, allow_bulk=True),

            unless_allowed_by_qualification_milestone(
                validate_bid_document_in_tender_status,
                validate_bid_document_operation_in_award_status,
            ),
            validate_bid_document_operation_period,
            validate_bid_document_operation_in_bid_status,
        ),
        permission="edit_bid",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        validators=(
            validate_item_owner("bid"),
            validate_input_data(PostDocument),

            unless_allowed_by_qualification_milestone(
                validate_bid_document_in_tender_status,
                validate_bid_document_operation_in_award_status,
            ),
            validate_bid_document_operation_period,
            validate_update_bid_document_confidentiality,

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
        return super().patch()


@resource(
    name="{}:Tender Bid Documents".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA bidder documents",
)
class UATenderBidDocumentResource(EUTenderBidDocumentResource):
    pass
