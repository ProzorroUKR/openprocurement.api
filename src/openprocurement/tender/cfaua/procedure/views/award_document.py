from openprocurement.tender.core.procedure.views.award_document import BaseAwardDocumentResource
from openprocurement.tender.core.procedure.models.document import PostDocument, PatchDocument, Document
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    validate_patch_data,
    validate_item_owner,
    unless_bots,
    update_doc_fields_on_put_document,
    validate_upload_document,
    validate_data_model,
    validate_award_document_tender_not_in_allowed_status_base,
    validate_award_document_lot_not_in_allowed_status,
    validate_award_document_author,
)
from openprocurement.tender.cfaua.procedure.validation import validate_award_document_tender_not_in_allowed_status
from openprocurement.tender.openua.procedure.validation import validate_accepted_complaints
from openprocurement.api.utils import json_view
from cornice.resource import resource


@resource(
    name="closeFrameworkAgreementUA:Tender Award Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender award documents",
)
class CFAUATenderAwardDocumentResource(BaseAwardDocumentResource):

    @json_view(
        validators=(
            unless_bots(validate_item_owner("tender")),
            validate_input_data(PostDocument, allow_bulk=True),
            validate_award_document_tender_not_in_allowed_status,
            validate_award_document_lot_not_in_allowed_status,
            validate_accepted_complaints,
        ),
        permission="upload_award_documents",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        validators=(
            validate_item_owner("tender"),
            validate_input_data(PostDocument),
            validate_award_document_tender_not_in_allowed_status_base,
            validate_award_document_lot_not_in_allowed_status,
            validate_award_document_author,
            validate_accepted_complaints,

            update_doc_fields_on_put_document,
            validate_upload_document,
            validate_data_model(Document),
        ),
        permission="upload_award_documents",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        validators=(
            validate_item_owner("tender"),
            validate_input_data(PatchDocument, none_means_remove=True),
            validate_patch_data(Document, item_name="document"),
            validate_award_document_tender_not_in_allowed_status_base,
            validate_award_document_lot_not_in_allowed_status,
            validate_award_document_author,
            validate_accepted_complaints,
        ),
        permission="edit_award_documents",
    )
    def patch(self):
        return super().patch()
