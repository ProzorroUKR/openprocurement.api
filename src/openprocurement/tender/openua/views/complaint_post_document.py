# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    get_file,
    upload_file,
    update_file_content_type,
    json_view,
    context_unpack,
    APIResource,
)
from openprocurement.api.validation import (
    validate_file_update,
    validate_file_upload,
    validate_patch_document_data,
)

from openprocurement.tender.core.validation import (
    validate_complaint_document_update_not_by_author,
)

from openprocurement.tender.core.utils import save_tender, optendersresource, apply_patch
from openprocurement.tender.openua.validation import (
    validate_complaint_post_review_date,
    validate_complaint_post_complaint_status,
    validate_complaint_post_document_upload_by_author,
)


@optendersresource(
    name="aboveThresholdUA:Tender Complaint Post Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender complaint post documents",
)
class TenderComplaintPostDocumentResource(APIResource):
    @json_view(permission="view_tender")
    def collection_get(self):
        """
        Tender Complaint Post Documents List
        """
        if self.request.params.get("all", ""):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(
                dict([(i.id, i.serialize("view")) for i in self.context.documents]).values(),
                key=lambda i: i["dateModified"],
            )
        return {"data": collection_data}

    @json_view(
        validators=(
            validate_file_upload,
            validate_complaint_post_document_upload_by_author,
            validate_complaint_post_complaint_status,
            validate_complaint_post_review_date,
        ),
        permission="edit_complaint",
    )
    def collection_post(self):
        """
        Tender Complaint Post Document Upload
        """
        document = upload_file(self.request)
        document.author = self.request.authenticated_role
        self.context.documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender complaint post document {}".format(document.id),
                extra=context_unpack(
                    self.request, {"MESSAGE_ID": "tender_complaint_post_document_create"},
                    {"document_id": document.id}
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
        """
        Tender Complaint Post Document Read
        """
        if self.request.params.get("download"):
            return get_file(self.request)
        document = self.request.validated["document"]
        document_data = document.serialize("view")
        document_data["previousVersions"] = [
            i.serialize("view") for i in self.request.validated["documents"] if i.url != document.url
        ]
        return {"data": document_data}

    @json_view(
        validators=(
            validate_file_update,
            validate_complaint_document_update_not_by_author,
            validate_complaint_post_complaint_status,
            validate_complaint_post_review_date,
        ),
        permission="edit_complaint",
    )
    def put(self):
        """
        Tender Complaint Post Document Update
        """
        document = upload_file(self.request)
        document.author = self.request.authenticated_role
        self.request.validated["post"].documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender complaint document {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_complaint_post_document_put"}),
            )
            return {"data": document.serialize("view")}

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_document_data,
            validate_complaint_document_update_not_by_author,
            validate_complaint_post_complaint_status,
            validate_complaint_post_review_date,
        ),
        permission="edit_complaint",
    )
    def patch(self):
        """
        Tender Complaint Post Document Update
        """
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info(
                "Updated tender complaint document {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_complaint_post_document_patch"}),
            )
            return {"data": self.request.context.serialize("view")}
