# -*- coding: utf-8 -*-
from openprocurement.tender.belowthreshold.views.award_complaint_document import TenderAwardComplaintDocumentResource
from openprocurement.api.utils import (
    context_unpack,
    json_view,
    update_file_content_type,
    upload_file,
    raise_operation_error,
    error_handler,
)
from openprocurement.tender.core.utils import save_tender, optendersresource, apply_patch
from openprocurement.api.validation import validate_file_update, validate_file_upload, validate_patch_document_data
from openprocurement.tender.openua.constants import STATUS4ROLE


@optendersresource(
    name="aboveThresholdUA:Tender Award Complaint Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender award complaint documents",
)
class TenderUaAwardComplaintDocumentResource(TenderAwardComplaintDocumentResource):
    def validate_complaint_document(self, operation):
        """ TODO move validators
        This class is inherited in limited and openeu (qualification complaint) package, but validate_complaint_document function has different validators.
        For now, we have no way to use different validators on methods according to procedure type.
        """
        if operation == "update" and self.request.authenticated_role != self.context.author:
            self.request.errors.add("url", "role", "Can update document only author")
            self.request.errors.status = 403
            raise error_handler(self.request.errors)
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
                if i.id == self.request.validated["award"].lotID
            ]
        ):
            raise_operation_error(self.request, "Can {} document only in active lot status".format(operation))
        if self.request.validated["complaint"].status not in STATUS4ROLE.get(self.request.authenticated_role, []):
            raise_operation_error(
                self.request,
                "Can't {} document in current ({}) complaint status".format(
                    operation, self.request.validated["complaint"].status
                ),
            )
        return True

    @json_view(permission="edit_complaint", validators=(validate_file_upload,))
    def collection_post(self):
        """Tender Award Complaint Document Upload
        """
        if not self.validate_complaint_document("add"):
            return
        document = upload_file(self.request)
        document.author = self.request.authenticated_role
        self.context.documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender award complaint document {}".format(document.id),
                extra=context_unpack(
                    self.request, {"MESSAGE_ID": "tender_award_complaint_document_create"}, {"document_id": document.id}
                ),
            )
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers["Location"] = self.request.current_route_url(
                _route_name=document_route, document_id=document.id, _query={}
            )
            return {"data": document.serialize("view")}

    @json_view(validators=(validate_file_update,), permission="edit_complaint")
    def put(self):
        """Tender Award Complaint Document Update"""
        if not self.validate_complaint_document("update"):
            return
        document = upload_file(self.request)
        document.author = self.request.authenticated_role
        self.request.validated["complaint"].documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender award complaint document {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_award_complaint_document_put"}),
            )
            return {"data": document.serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_document_data,), permission="edit_complaint")
    def patch(self):
        """Tender Award Complaint Document Update"""
        if not self.validate_complaint_document("update"):
            return
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info(
                "Updated tender award complaint document {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_award_complaint_document_patch"}),
            )
            return {"data": self.request.context.serialize("view")}
