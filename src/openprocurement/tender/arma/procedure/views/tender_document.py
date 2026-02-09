from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    update_doc_fields_on_put_document,
    validate_data_model,
    validate_input_data,
    validate_item_owner,
    validate_patch_data,
    validate_upload_document,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.state.tender_document import (
    TenderDocumentState,
)
from openprocurement.tender.core.procedure.models.document import (
    Document,
    PatchDocument,
    PostDocument,
)
from openprocurement.tender.core.procedure.validation import (
    unless_bots_or_auction,
    validate_document_operation_in_allowed_tender_statuses,
    validate_tender_document_update_not_by_author_or_tender_owner,
)
from openprocurement.tender.core.procedure.views.tender_document import (
    TenderDocumentResource as BaseTenderDocumentResource,
)

validate_tender_document_operation_in_allowed_tender_statuses = validate_document_operation_in_allowed_tender_statuses(
    ("draft", "active.tendering", "active.pre-qualification")
)


@resource(
    name="complexAsset.arma:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender related binary files (PDFs, etc.)",
)
class TenderDocumentResource(BaseTenderDocumentResource):
    state_class = TenderDocumentState

    @json_view(
        validators=(
            unless_bots_or_auction(validate_item_owner("tender")),
            validate_input_data(PostDocument, allow_bulk=True),
            validate_tender_document_operation_in_allowed_tender_statuses,
        ),
        permission="upload_tender_documents",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        validators=(
            unless_bots_or_auction(validate_item_owner("tender")),
            validate_input_data(PostDocument),
            update_doc_fields_on_put_document,
            validate_tender_document_operation_in_allowed_tender_statuses,
            validate_tender_document_update_not_by_author_or_tender_owner,
            validate_upload_document,
            validate_data_model(Document),
        ),
        permission="upload_tender_documents",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        validators=(
            unless_bots_or_auction(validate_item_owner("tender")),
            validate_input_data(PatchDocument, none_means_remove=True),
            validate_patch_data(Document, item_name="document"),
            validate_tender_document_operation_in_allowed_tender_statuses,
            validate_tender_document_update_not_by_author_or_tender_owner,
        ),
        permission="upload_tender_documents",
    )
    def patch(self):
        return super().patch()
