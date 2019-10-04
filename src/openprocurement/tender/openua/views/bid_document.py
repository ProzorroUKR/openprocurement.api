# -*- coding: utf-8 -*-
from openprocurement.api.utils import upload_file, update_file_content_type, json_view, context_unpack, get_now
from openprocurement.api.validation import validate_file_update, validate_file_upload, validate_patch_document_data
from openprocurement.tender.core.validation import (
    validate_bid_document_operation_period,
    validate_bid_document_operation_with_award,
    validate_bid_document_operation_in_not_allowed_status,
)
from openprocurement.tender.belowthreshold.views.bid_document import TenderBidDocumentResource
from openprocurement.tender.core.utils import save_tender, apply_patch, optendersresource


@optendersresource(
    name="aboveThresholdUA:Tender Bid Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender UA bidder documents",
)
class TenderUaBidDocumentResource(TenderBidDocumentResource):
    @json_view(
        validators=(
            validate_file_upload,
            validate_bid_document_operation_in_not_allowed_status,
            validate_bid_document_operation_period,
            validate_bid_document_operation_with_award,
        ),
        permission="edit_bid",
    )
    def collection_post(self):
        """Tender Bid Document Upload
        """
        document = upload_file(self.request)
        self.context.documents.append(document)
        if self.request.validated["tender_status"] == "active.tendering":
            self.request.validated["tender"].modified = False
        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender bid document {}".format(document.id),
                extra=context_unpack(
                    self.request, {"MESSAGE_ID": "tender_bid_document_create"}, {"document_id": document.id}
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
            validate_bid_document_operation_in_not_allowed_status,
            validate_bid_document_operation_period,
            validate_bid_document_operation_with_award,
        ),
        permission="edit_bid",
    )
    def put(self):
        """Tender Bid Document Update"""
        document = upload_file(self.request)
        self.request.validated["bid"].documents.append(document)
        if self.request.validated["tender_status"] == "active.tendering":
            self.request.validated["tender"].modified = False
        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender bid document {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_bid_document_put"}),
            )
            return {"data": document.serialize("view")}

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_document_data,
            validate_bid_document_operation_in_not_allowed_status,
            validate_bid_document_operation_period,
            validate_bid_document_operation_with_award,
        ),
        permission="edit_bid",
    )
    def patch(self):
        """Tender Bid Document Update"""
        if self.request.validated["tender_status"] == "active.tendering":
            self.request.validated["tender"].modified = False
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info(
                "Updated tender bid document {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_bid_document_patch"}),
            )
            return {"data": self.request.context.serialize("view")}
