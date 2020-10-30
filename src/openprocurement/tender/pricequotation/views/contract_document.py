# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    upload_file,
    update_file_content_type,
    json_view,
    context_unpack,
)
from openprocurement.api.validation import\
    validate_file_update, validate_patch_document_data, validate_file_upload
from openprocurement.tender.core.utils import\
    save_tender, optendersresource, apply_patch
from openprocurement.tender.core.validation import (
    validate_role_for_contract_document_operation,
    validate_relatedItem_for_contract_document_uploading,
    validate_contract_supplier_role_for_contract_document_uploading,
)
from openprocurement.tender.belowthreshold.views.contract_document\
    import TenderAwardContractDocumentResource
from openprocurement.tender.pricequotation.constants import PMT
from openprocurement.tender.pricequotation.validation import\
    validate_contract_document


@optendersresource(
    name="{}:Tender Contract Documents".format(PMT),
    collection_path="/tenders/{tender_id}/contracts/{contract_id}/documents",
    path="/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}",
    procurementMethodType=PMT,
    description="Tender contract documents",
)
class PQTenderAwardContractDocumentResource(TenderAwardContractDocumentResource):

    @json_view(
        permission="upload_contract_documents",
        validators=(
            validate_file_upload,
            validate_role_for_contract_document_operation,
            validate_contract_document,
            validate_contract_supplier_role_for_contract_document_uploading,
            validate_relatedItem_for_contract_document_uploading,
        )
    )
    def collection_post(self):
        """Tender Contract Document Upload
        """
        document = upload_file(self.request)
        document.author = self.request.authenticated_role
        self.context.documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender contract document {}".format(document.id),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_contract_document_create"},
                    {"document_id": document.id}
                ),
            )
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers["Location"] = self.request.current_route_url(
                _route_name=document_route, document_id=document.id, _query={}
            )
            return {"data": document.serialize("view")}

    @json_view(
        validators=(
            validate_file_update,
            validate_role_for_contract_document_operation,
            validate_contract_document,
            validate_contract_supplier_role_for_contract_document_uploading,
            validate_relatedItem_for_contract_document_uploading,
        ),
        permission="upload_contract_documents"
    )
    def put(self):
        """Tender Contract Document Update"""
        document = upload_file(self.request)
        document.author = self.request.authenticated_role
        self.request.validated["contract"].documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender contract document {}".format(self.request.context.id),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_contract_document_put"}
                ),
            )
            return {"data": document.serialize("view")}

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_document_data,
            validate_role_for_contract_document_operation,
            validate_contract_document,
            validate_contract_supplier_role_for_contract_document_uploading,
            validate_relatedItem_for_contract_document_uploading,
        ),
        permission="upload_contract_documents"
    )
    def patch(self):
        """Tender Contract Document Update"""
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info(
                "Updated tender contract document {}".format(self.request.context.id),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_contract_document_patch"}
                ),
            )
            return {"data": self.request.context.serialize("view")}
