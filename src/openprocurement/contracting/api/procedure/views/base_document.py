from openprocurement.api.utils import json_view

from openprocurement.tender.core.procedure.serializers.document import DocumentSerializer
from openprocurement.contracting.api.procedure.models.document import Document, PostDocument, PatchDocument
from openprocurement.tender.core.procedure.documents import get_file
from openprocurement.tender.core.procedure.views.document import DocumentResourceMixin
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    validate_patch_data,
    validate_item_owner,
    unless_admins,
    update_doc_fields_on_put_document,
    validate_upload_document,
    validate_data_model,
)
from openprocurement.contracting.api.procedure.utils import save_contract
from openprocurement.contracting.api.procedure.state.document import BaseDocumentState
from openprocurement.contracting.api.procedure.views.base import ContractBaseResource
from openprocurement.contracting.api.procedure.validation import (
    validate_contract_document_operation_not_in_allowed_contract_status,
    validate_add_document_to_active_change,
)


class BaseDocumentResource(DocumentResourceMixin, ContractBaseResource):
    state_class = BaseDocumentState
    serializer_class = DocumentSerializer
    container = "documents"
    item_name = "contract"

    def save(self, **kwargs):
        return save_contract(self.request, **kwargs)

    def get_file(self):
        return get_file(self.request, item_name="contract")

    @json_view(permission="view_contract")
    def collection_get(self):
        return super().collection_get()

    @json_view(
        validators=(
            unless_admins(validate_item_owner("contract")),
            validate_input_data(PostDocument, allow_bulk=True),
            validate_contract_document_operation_not_in_allowed_contract_status,
        ),
        permission="upload_contract_documents",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(permission="view_contract")
    def get(self):
        return super().get()

    @json_view(
        validators=(
            unless_admins(validate_item_owner("contract")),
            validate_input_data(PostDocument),

            update_doc_fields_on_put_document,
            validate_upload_document,
            validate_data_model(Document),
            validate_contract_document_operation_not_in_allowed_contract_status,
        ),
        permission="edit_contract_documents",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        validators=(
            unless_admins(validate_item_owner("contract")),
            validate_input_data(PatchDocument, none_means_remove=True),
            validate_patch_data(Document, item_name="document"),
            validate_contract_document_operation_not_in_allowed_contract_status,
            validate_add_document_to_active_change,
        ),
        permission="edit_contract_documents",
    )
    def patch(self):
        return super().patch()
