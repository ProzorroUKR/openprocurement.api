from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    unless_bots,
    update_doc_fields_on_put_document,
    validate_data_model,
    validate_input_data,
    validate_item_owner,
    validate_patch_data,
    validate_upload_document,
)
from openprocurement.api.utils import json_view, raise_operation_error
from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.models.document import (
    Document,
    PatchDocument,
    PostDocument,
)
from openprocurement.tender.core.procedure.validation import (
    OPERATIONS,
    validate_award_document_author,
    validate_award_document_lot_not_in_allowed_status,
)
from openprocurement.tender.core.procedure.views.award_document import (
    BaseAwardDocumentResource,
)


def validate_award_document_tender_not_in_allowed_tender_status(request, allowed_bot_statuses=("active.awarded",), **_):
    allowed_tender_statuses = ["active.qualification", "active.awarded"]
    if request.authenticated_role == "bots":
        allowed_tender_statuses.extend(allowed_bot_statuses)
    status = request.validated["tender"]["status"]
    if status not in allowed_tender_statuses:
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document in current ({status}) tender status",
        )


@resource(
    name="complexAsset.arma:Tender Award Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender award documents",
)
class TenderAwardDocumentResource(BaseAwardDocumentResource):
    @json_view(
        validators=(
            unless_bots(validate_item_owner("tender")),
            validate_input_data(PostDocument, allow_bulk=True),
            validate_award_document_tender_not_in_allowed_tender_status,
            validate_award_document_lot_not_in_allowed_status,
        ),
        permission="upload_award_documents",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        validators=(
            validate_item_owner("tender"),
            validate_input_data(PostDocument),
            validate_award_document_tender_not_in_allowed_tender_status,
            validate_award_document_lot_not_in_allowed_status,
            validate_award_document_author,
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
            validate_award_document_tender_not_in_allowed_tender_status,
            validate_award_document_lot_not_in_allowed_status,
            validate_award_document_author,
        ),
        permission="edit_award_documents",
    )
    def patch(self):
        return super().patch()
