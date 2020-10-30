# -*- coding: utf-8 -*-
from openprocurement.api.utils import (APIResource, context_unpack, get_file, json_view, update_file_content_type,
                                       upload_file)
from openprocurement.api.validation import validate_file_update, validate_file_upload, validate_patch_document_data
from openprocurement.tender.belowthreshold.validation import validate_document_operation_in_not_allowed_tender_status
from openprocurement.tender.core.utils import apply_patch, optendersresource, save_tender
from openprocurement.tender.core.validation import (validate_patch_document_contract_proforma,
                                                    validate_tender_document_update_not_by_author_or_tender_owner)


@optendersresource(
    name="belowThreshold:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType="belowThreshold",
    description="Tender related binary files (PDFs, etc.)",
)
class TenderDocumentResource(APIResource):
    @json_view(permission="view_tender")
    def collection_get(self):
        """Tender Documents List"""
        if self.request.params.get("all", ""):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(
                dict([(i.id, i.serialize("view")) for i in self.context.documents]).values(),
                key=lambda i: i["dateModified"],
            )
        return {"data": collection_data}

    @json_view(
        permission="upload_tender_documents",
        validators=(validate_file_upload, validate_document_operation_in_not_allowed_tender_status),
    )
    def collection_post(self):
        """Tender Document Upload"""
        document = upload_file(self.request)
        document.author = self.request.authenticated_role
        self.context.documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender document {}".format(document.id),
                extra=context_unpack(
                    self.request, {"MESSAGE_ID": "tender_document_create"}, {"document_id": document.id}
                ),
            )
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers["Location"] = self.request.current_route_url(
                _route_name=document_route, document_id=document.id, _query={}
            )
            return {"data": document.serialize("view")}

    @json_view(permission="view_tender")
    def get(self):
        """Tender Document Read"""
        if self.request.params.get("download"):
            return get_file(self.request)
        document = self.request.validated["document"]
        document_data = document.serialize("view")
        document_data["previousVersions"] = [
            i.serialize("view") for i in self.request.validated["documents"] if i.url != document.url
        ]
        return {"data": document_data}

    @json_view(
        permission="upload_tender_documents",
        validators=(
            validate_file_update,
            validate_document_operation_in_not_allowed_tender_status,
            validate_tender_document_update_not_by_author_or_tender_owner,
        ),
    )
    def put(self):
        """Tender Document Update"""
        document = upload_file(self.request)
        self.request.validated["tender"].documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender document {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_document_put"}),
            )
            return {"data": document.serialize("view")}

    @json_view(
        content_type="application/json",
        permission="upload_tender_documents",
        validators=(
            validate_patch_document_data,
            validate_patch_document_contract_proforma,
            validate_document_operation_in_not_allowed_tender_status,
            validate_tender_document_update_not_by_author_or_tender_owner,
        ),
    )
    def patch(self):
        """Tender Document Update"""
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info(
                "Updated tender document {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_document_patch"}),
            )
            return {"data": self.request.context.serialize("view")}
