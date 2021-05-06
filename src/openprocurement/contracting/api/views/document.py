# -*- coding: utf-8 -*-
from openprocurement.api.views.document import BaseDocumentResource
from openprocurement.contracting.api.utils import save_contract, contractingresource, apply_patch
from openprocurement.api.utils import (
    context_unpack,
    json_view,
)
from openprocurement.api.validation import (
    validate_file_update,
    validate_patch_document_data,
    validate_file_upload,
)
from openprocurement.contracting.api.validation import (
    validate_add_document_to_active_change,
    validate_contract_document_operation_not_in_allowed_contract_status,
    validate_file_transaction_upload,
)
from openprocurement.contracting.api.utils import get_transaction_by_id, upload_file_to_transaction


class CoreDocumentResource(BaseDocumentResource):
    container = "documents"
    context_name = "contract"
    db_key = "contracts"

    def save(self, request, **kwargs):
        return save_contract(request)

    def apply(self, request, **kwargs):
        return apply_patch(request, **kwargs)


@contractingresource(
    name="Contract Documents",
    collection_path="/contracts/{contract_id}/documents",
    path="/contracts/{contract_id}/documents/{document_id}",
    description="Contract related binary files (PDFs, etc.)",
)
class ContractsDocumentResource(CoreDocumentResource):
    @json_view(permission="view_contract")
    def collection_get(self):
        """Contract Documents List"""
        return super(ContractsDocumentResource, self).collection_get()

    @json_view(
        permission="upload_contract_documents",
        validators=(validate_file_upload, validate_contract_document_operation_not_in_allowed_contract_status),
    )
    def collection_post(self):
        """Contract Document Upload"""
        return super(ContractsDocumentResource, self).collection_post()

    @json_view(permission="view_contract")
    def get(self):
        """Contract Document Read"""
        return super(ContractsDocumentResource, self).get()

    @json_view(
        permission="upload_contract_documents",
        validators=(validate_file_update, validate_contract_document_operation_not_in_allowed_contract_status),
    )
    def put(self):
        """Contract Document Update"""
        return super(ContractsDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        permission="upload_contract_documents",
        validators=(
            validate_patch_document_data,
            validate_contract_document_operation_not_in_allowed_contract_status,
            validate_add_document_to_active_change,
        ),
    )
    def patch(self):
        """Contract Document Update"""
        return super(ContractsDocumentResource, self).patch()


@contractingresource(
    name="Contract Transaction Documents",
    path="/contracts/{contract_id}/transactions/{transaction_id}/documents",
    description="Contract transaction related binary files (PDFs, etc.)",
)
class ContractTransactionDocumentResource(BaseDocumentResource):
    @json_view(
        content_type="application/json",
        permission="upload_contract_transaction_documents",
        validators=(validate_file_transaction_upload,),
    )
    def post(self):
        """Contract Transaction Document Upload"""
        document = upload_file_to_transaction(self.request)
        _transaction = get_transaction_by_id(self.request)
        _transaction.documents.append(document)
        if save_contract(self.request):
            self.LOGGER.info(
                "Created contract transaction document {}".format(document.id),
                extra=context_unpack(
                    self.request, {"MESSAGE_ID": "contract_transaction_document_create"}, {"document_id": document.id}
                ),
            )

            self.request.response.status = 201
            return {"data": document.serialize("view")}
