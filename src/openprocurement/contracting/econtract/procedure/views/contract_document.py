from cornice.resource import resource

from openprocurement.contracting.core.procedure.views.contract_document import ContractDocumentResource
from openprocurement.api.utils import json_view

from openprocurement.contracting.econtract.procedure.models.document import Document, PostDocument, PatchDocument
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    validate_patch_data,
    unless_admins,
    update_doc_fields_on_put_document,
    validate_upload_document,
    validate_data_model,
)
from openprocurement.contracting.core.procedure.validation import (
    validate_contract_owner,
    validate_contract_document_operation_not_in_allowed_contract_status,
    validate_add_document_to_active_change,
)


@resource(
    name="EContract Documents",
    collection_path="/contracts/{contract_id}/documents",
    path="/contracts/{contract_id}/documents/{document_id}",
    contractType="econtract",
    description="EContract related binary files (PDFs, etc.)",
)
class EContractDocumentResource(ContractDocumentResource):
    @json_view(
        validators=(
            unless_admins(validate_contract_owner),
            validate_input_data(PostDocument, allow_bulk=True),
            validate_contract_document_operation_not_in_allowed_contract_status,
        ),
        permission="upload_contract_documents",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        validators=(
            unless_admins(validate_contract_owner),
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
                unless_admins(validate_contract_owner),
                validate_input_data(PatchDocument, none_means_remove=True),
                validate_patch_data(Document, item_name="document"),
                validate_contract_document_operation_not_in_allowed_contract_status,
                validate_add_document_to_active_change,
        ),
        permission="edit_contract_documents",
    )
    def patch(self):
        return super().patch()
