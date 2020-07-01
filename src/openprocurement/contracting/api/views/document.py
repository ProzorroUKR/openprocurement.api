# -*- coding: utf-8 -*-
from openprocurement.contracting.api.utils import save_contract, contractingresource, apply_patch
from openprocurement.api.utils import (
    upload_file,
    update_file_content_type,
    get_file,
    context_unpack,
    APIResource,
    json_view,
)
from openprocurement.api.validation import validate_file_update, validate_file_upload, validate_patch_document_data
from openprocurement.contracting.api.validation import (
    validate_add_document_to_active_change,
    validate_contract_document_operation_not_in_allowed_contract_status,
    validate_file_transaction_upload,
)
from openprocurement.contracting.api.utils import get_transaction_by_id, upload_file_to_transaction


@contractingresource(
    name="Contract Documents",
    collection_path="/contracts/{contract_id}/documents",
    path="/contracts/{contract_id}/documents/{document_id}",
    description="Contract related binary files (PDFs, etc.)",
)
class ContractsDocumentResource(APIResource):
    @json_view(permission="view_contract")
    def collection_get(self):
        """Contract Documents List"""
        if self.request.params.get("all", ""):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(
                dict([(i.id, i.serialize("view")) for i in self.context.documents]).values(),
                key=lambda i: i["dateModified"],
            )
        return {"data": collection_data}

    @json_view(
        permission="upload_contract_documents",
        validators=(validate_file_upload, validate_contract_document_operation_not_in_allowed_contract_status),
    )
    def collection_post(self):
        """Contract Document Upload"""
        document = upload_file(self.request)
        self.context.documents.append(document)
        if save_contract(self.request):
            self.LOGGER.info(
                "Created contract document {}".format(document.id),
                extra=context_unpack(
                    self.request, {"MESSAGE_ID": "contract_document_create"}, {"document_id": document.id}
                ),
            )
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers["Location"] = self.request.current_route_url(
                _route_name=document_route, document_id=document.id, _query={}
            )
            return {"data": document.serialize("view")}

    @json_view(permission="view_contract")
    def get(self):
        """Contract Document Read"""
        if self.request.params.get("download"):
            return get_file(self.request)
        document = self.request.validated["document"]
        document_data = document.serialize("view")
        document_data["previousVersions"] = [
            i.serialize("view") for i in self.request.validated["documents"] if i.url != document.url
        ]
        return {"data": document_data}

    @json_view(
        permission="upload_contract_documents",
        validators=(validate_file_update, validate_contract_document_operation_not_in_allowed_contract_status),
    )
    def put(self):
        """Contract Document Update"""
        document = upload_file(self.request)
        self.request.validated["contract"].documents.append(document)
        if save_contract(self.request):
            self.LOGGER.info(
                "Updated contract document {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "contract_document_put"}),
            )
            return {"data": document.serialize("view")}

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
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info(
                "Updated contract document {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "contract_document_patch"}),
            )
            return {"data": self.request.context.serialize("view")}


@contractingresource(
    name="Contract Transaction Documents",
    path="/contracts/{contract_id}/transactions/{transaction_id}/documents",
    description="Contract transaction related binary files (PDFs, etc.)",
)
class ContractTransactionDocumentResource(APIResource):

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
