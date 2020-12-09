# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    upload_file,
    update_file_content_type,
    get_file,
    context_unpack,
    APIResource,
    json_view,
)
from openprocurement.api.validation import validate_file_update, validate_file_upload, validate_patch_document_data
from openprocurement.framework.core.utils import save_qualification, apply_patch, qualificationsresource
from openprocurement.framework.core.validation import (
    validate_document_operation_in_not_allowed_status
)


@qualificationsresource(
    name="electronicCatalogue: Qualification Documents",
    collection_path="/qualifications/{qualification_id}/documents",
    path="/qualifications/{qualification_id}/documents/{document_id}",
    description="Qualification related binary files (PDFs, etc.)",
)
class QualificationDocumentResource(APIResource):
    @json_view(permission="view_qualification")
    def collection_get(self):
        """Qualification Documents List"""
        if self.request.params.get("all", ""):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(
                dict([(i.id, i.serialize("view")) for i in self.context.documents]).values(),
                key=lambda i: i["dateModified"],
            )
        return {"data": collection_data}

    @json_view(
        permission="edit_qualification",
        validators=(
            validate_document_operation_in_not_allowed_status,
            validate_file_upload,
        ),
    )
    def collection_post(self):
        """Qualification Document Upload"""
        document = upload_file(self.request)
        self.context.documents.append(document)
        if save_qualification(self.request):
            self.LOGGER.info(
                "Created qualification document {}".format(document.id),
                extra=context_unpack(
                    self.request, {"MESSAGE_ID": "qualification_document_create"}, {"document_id": document.id}
                ),
            )
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers["Location"] = self.request.current_route_url(
                _route_name=document_route, document_id=document.id, _query={}
            )
            return {"data": document.serialize("view")}

    @json_view(permission="view_qualification")
    def get(self):
        """qualification Document Read"""
        if self.request.params.get("download"):
            return get_file(self.request)
        document = self.request.validated["document"]
        document_data = document.serialize("view")
        document_data["previousVersions"] = [
            i.serialize("view") for i in self.request.validated["documents"] if i.url != document.url
        ]
        return {"data": document_data}

    @json_view(
        permission="edit_qualification",
        validators=(
            validate_document_operation_in_not_allowed_status,
            validate_file_update,
        ),
    )
    def put(self):
        """Qualification Document Update"""
        document = upload_file(self.request)
        self.request.validated["qualification"].documents.append(document)
        if save_qualification(self.request):
            self.LOGGER.info(
                "Updated qualification document {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "qualification_document_put"}),
            )
            return {"data": document.serialize("view")}

    @json_view(
        content_type="application/json",
        permission="edit_qualification",
        validators=(
            validate_document_operation_in_not_allowed_status,
            validate_patch_document_data,
        ),
    )
    def patch(self):
        """Qualification Document Update"""
        if apply_patch(self.request, src=self.request.context.serialize(), obj_name="qualification"):
            update_file_content_type(self.request)
            self.LOGGER.info(
                "Updated qualification document {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "qualification_document_patch"}),
            )
            return {"data": self.request.context.serialize("view")}
