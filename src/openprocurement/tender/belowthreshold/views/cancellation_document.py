# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    get_now,
    get_file,
    upload_file,
    update_file_content_type,
    json_view,
    context_unpack,
    APIResource,
)
from openprocurement.api.validation import validate_file_update, validate_file_upload, validate_patch_document_data

from openprocurement.tender.core.utils import (
    save_tender,
    optendersresource,
    apply_patch,
)

from openprocurement.tender.core.validation import (
    validate_cancellation_operation_document,
    validate_operation_cancellation_permission,
)
from openprocurement.tender.belowthreshold.validation import (
    validate_cancellation_document_operation_not_in_allowed_status,
)


@optendersresource(
    name="belowThreshold:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType="belowThreshold",
    description="Tender cancellation documents",
)
class TenderCancellationDocumentResource(APIResource):
    @json_view(permission="view_tender")
    def collection_get(self):
        """Tender Cancellation Documents List"""
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
            validate_cancellation_document_operation_not_in_allowed_status,
            validate_operation_cancellation_permission,
            validate_cancellation_operation_document,
        ),
        permission="edit_cancellation",
    )
    def collection_post(self):
        """Tender Cancellation Document Upload
        """
        document = upload_file(self.request)
        self.context.documents.append(document)

        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender cancellation document {}".format(document.id),
                extra=context_unpack(
                    self.request, {"MESSAGE_ID": "tender_cancellation_document_create"}, {"document_id": document.id}
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
        """Tender Cancellation Document Read"""
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
            validate_cancellation_document_operation_not_in_allowed_status,
            validate_operation_cancellation_permission,
            validate_cancellation_operation_document,
        ),
        permission="edit_cancellation",
    )
    def put(self):
        """Tender Cancellation Document Update"""
        document = upload_file(self.request)
        self.request.validated["cancellation"].documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender cancellation document {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_cancellation_document_put"}),
            )
            return {"data": document.serialize("view")}

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_document_data,
            validate_cancellation_document_operation_not_in_allowed_status,
            validate_operation_cancellation_permission,
            validate_cancellation_operation_document,
        ),
        permission="edit_cancellation",
    )
    def patch(self):
        """Tender Cancellation Document Update"""
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info(
                "Updated tender cancellation document {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_cancellation_document_patch"}),
            )
            return {"data": self.request.context.serialize("view")}
