from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.cfaua.procedure.models.document import PostDocument, PatchDocument, Document
from openprocurement.framework.cfaua.procedure.state.document import AgreementDocumentState
from openprocurement.framework.cfaua.procedure.views.base import AgreementBaseResource
from openprocurement.framework.core.procedure.validation import validate_document_operation_on_agreement_status
from openprocurement.framework.core.procedure.views.base import BaseDocumentResource
from openprocurement.framework.cfaua.constants import CFA_UA
from openprocurement.tender.core.procedure.serializers.document import DocumentSerializer
from openprocurement.api.procedure.validation import (
    validate_patch_data_simple,
    validate_data_model,
    validate_input_data, validate_item_owner, validate_upload_document, update_doc_fields_on_put_document,
)


@resource(
    name=f"{CFA_UA}:Agreement Documents",
    collection_path="/agreements/{agreement_id}/documents",
    path="/agreements/{agreement_id}/documents/{document_id}",
    agreementType=CFA_UA,
    description="Agreement Documents",
)
class AgreementDocumentsResource(AgreementBaseResource, BaseDocumentResource):
    item_name = "agreement"
    serializer_class = DocumentSerializer
    state_class = AgreementDocumentState

    @json_view(permission="view_agreement")
    def collection_get(self):
        return super().collection_get()

    @json_view(permission="view_agreement")
    def get(self):
        return super().get()

    @json_view(
        validators=(
                validate_item_owner("agreement"),
                validate_input_data(PostDocument, allow_bulk=True),
                validate_document_operation_on_agreement_status,
        ),
        permission="edit_agreement",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        validators=(
                validate_item_owner("agreement"),
                validate_input_data(PostDocument),
                update_doc_fields_on_put_document,
                validate_upload_document,
                validate_data_model(Document),
                validate_document_operation_on_agreement_status,
        ),
        permission="edit_agreement",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        validators=(
                validate_item_owner("agreement"),
                validate_input_data(PatchDocument, none_means_remove=True),
                validate_patch_data_simple(Document, item_name="document"),
                validate_document_operation_on_agreement_status,
        ),
        permission="edit_agreement",
    )
    def patch(self):
        return super().patch()
