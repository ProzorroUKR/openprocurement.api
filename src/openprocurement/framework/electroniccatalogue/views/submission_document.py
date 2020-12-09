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
from openprocurement.framework.core.utils import save_submission, apply_patch, submissionsresource
from openprocurement.framework.core.validation import (
    validate_document_operation_in_not_allowed_period
)


@submissionsresource(
    name="electronicCatalogue: Submission Documents",
    collection_path="/submissions/{submission_id}/documents",
    path="/submissions/{submission_id}/documents/{document_id}",
    description="Submission related binary files (PDFs, etc.)",
)
class SubmissionDocumentResource(APIResource):
    @json_view(permission="view_submission")
    def collection_get(self):
        """Submission Documents List"""
        if self.request.params.get("all", ""):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(
                dict([(i.id, i.serialize("view")) for i in self.context.documents]).values(),
                key=lambda i: i["dateModified"],
            )
        return {"data": collection_data}

    @json_view(
        permission="edit_submission",
        validators=(
            validate_document_operation_in_not_allowed_period,
            validate_file_upload,
        ),
    )
    def collection_post(self):
        """Submission Document Upload"""
        document = upload_file(self.request)
        self.context.documents.append(document)
        if save_submission(self.request):
            self.LOGGER.info(
                "Created submission document {}".format(document.id),
                extra=context_unpack(
                    self.request, {"MESSAGE_ID": "submission_document_create"}, {"document_id": document.id}
                ),
            )
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers["Location"] = self.request.current_route_url(
                _route_name=document_route, document_id=document.id, _query={}
            )
            return {"data": document.serialize("view")}

    @json_view(permission="view_submission")
    def get(self):
        """Submission Document Read"""
        if self.request.params.get("download"):
            return get_file(self.request)
        document = self.request.validated["document"]
        document_data = document.serialize("view")
        document_data["previousVersions"] = [
            i.serialize("view") for i in self.request.validated["documents"] if i.url != document.url
        ]
        return {"data": document_data}

    @json_view(
        permission="edit_submission",
        validators=(
            validate_document_operation_in_not_allowed_period,
            validate_file_update,
        ),
    )
    def put(self):
        """Submission Document Update"""
        document = upload_file(self.request)
        self.request.validated["submission"].documents.append(document)
        if save_submission(self.request):
            self.LOGGER.info(
                "Updated submission document {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "submission_document_put"}),
            )
            return {"data": document.serialize("view")}

    @json_view(
        content_type="application/json",
        permission="edit_submission",
        validators=(
            validate_document_operation_in_not_allowed_period,
            validate_patch_document_data,
        ),
    )
    def patch(self):
        """Submission Document Update"""
        if apply_patch(self.request, src=self.request.context.serialize(), obj_name="submission"):
            update_file_content_type(self.request)
            self.LOGGER.info(
                "Updated submission document {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "submission_document_patch"}),
            )
            return {"data": self.request.context.serialize("view")}
