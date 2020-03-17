# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    get_file,
    upload_file,
    update_file_content_type,
    json_view,
    context_unpack,
    APIResource,
    raise_operation_error,
)
from openprocurement.api.validation import validate_file_update, validate_file_upload, validate_patch_document_data

from openprocurement.tender.core.utils import save_tender, optendersresource, apply_patch


@optendersresource(
    name="belowThreshold:Tender Contract Documents",
    collection_path="/tenders/{tender_id}/contracts/{contract_id}/documents",
    path="/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}",
    procurementMethodType="belowThreshold",
    description="Tender contract documents",
)
class TenderAwardContractDocumentResource(APIResource):
    def validate_contract_document(self, operation):
        """ TODO move validators
        This class is inherited in openua package, but validate_contract_document function has different validators.
        For now, we have no way to use different validators on methods according to procedure type.
        """
        if self.request.validated["tender_status"] not in ["active.qualification", "active.awarded"]:
            raise_operation_error(
                self.request,
                "Can't {} document in current ({}) tender status".format(
                    operation, self.request.validated["tender_status"]
                ),
            )
        if any(
            [
                i.status != "active"
                for i in self.request.validated["tender"].lots
                if i.id
                in [
                    a.lotID
                    for a in self.request.validated["tender"].awards
                    if a.id == self.request.validated["contract"].awardID
                ]
            ]
        ):
            raise_operation_error(self.request, "Can {} document only in active lot status".format(operation))
        if self.request.validated["contract"].status not in ["pending", "active"]:
            raise_operation_error(self.request, "Can't {} document in current contract status".format(operation))
        return True

    @json_view(permission="view_tender")
    def collection_get(self):
        """Tender Contract Documents List"""
        if self.request.params.get("all", ""):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(
                dict([(i.id, i.serialize("view")) for i in self.context.documents]).values(),
                key=lambda i: i["dateModified"],
            )
        return {"data": collection_data}

    @json_view(permission="upload_contract_documents", validators=(validate_file_upload,))
    def collection_post(self):
        """Tender Contract Document Upload
        """
        if not self.validate_contract_document("add"):
            return
        document = upload_file(self.request)
        self.context.documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender contract document {}".format(document.id),
                extra=context_unpack(
                    self.request, {"MESSAGE_ID": "tender_contract_document_create"}, {"document_id": document.id}
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
        """Tender Contract Document Read"""
        if self.request.params.get("download"):
            return get_file(self.request)
        document = self.request.validated["document"]
        document_data = document.serialize("view")
        document_data["previousVersions"] = [
            i.serialize("view") for i in self.request.validated["documents"] if i.url != document.url
        ]
        return {"data": document_data}

    @json_view(validators=(validate_file_update,), permission="upload_contract_documents")
    def put(self):
        """Tender Contract Document Update"""
        if not self.validate_contract_document("update"):
            return
        document = upload_file(self.request)
        self.request.validated["contract"].documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender contract document {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_contract_document_put"}),
            )
            return {"data": document.serialize("view")}

    @json_view(content_type="application/json",
               validators=(validate_patch_document_data,),
               permission="upload_contract_documents")
    def patch(self):
        """Tender Contract Document Update"""
        if not self.validate_contract_document("update"):
            return
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info(
                "Updated tender contract document {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_contract_document_patch"}),
            )
            return {"data": self.request.context.serialize("view")}
