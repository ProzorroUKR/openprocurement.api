# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    raise_operation_error,
    error_handler,
    json_view,
)
from openprocurement.api.validation import (
    validate_file_upload,
    validate_file_update,
    validate_patch_document_data,
)
from openprocurement.tender.belowthreshold.views.award_complaint_document import (
    TenderAwardComplaintDocumentResource as BaseTenderAwardComplaintDocumentResource,
)
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.open.constants import STATUS4ROLE, ABOVE_THRESHOLD


@optendersresource(
    name=f"{ABOVE_THRESHOLD}:Tender Award Complaint Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    description="Tender award complaint documents",
)
class TenderAwardComplaintDocumentResource(BaseTenderAwardComplaintDocumentResource):
    def validate_complaint_document(self, operation):
        """ TODO move validators
        This class is inherited in limited and openeu (qualification complaint) package, but validate_complaint_document function has different validators.
        For now, we have no way to use different validators on methods according to procedure type.
        """
        if operation == "update" and self.request.authenticated_role != self.context.author:
            self.request.errors.add("url", "role", "Can update document only author")
            self.request.errors.status = 403
            raise error_handler(self.request)
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
        return super(TenderAwardComplaintDocumentResource, self).collection_post()

    @json_view(validators=(validate_file_update,), permission="edit_complaint")
    def put(self):
        """Tender Award Complaint Document Update"""
        if not self.validate_complaint_document("update"):
            return
        return super(TenderAwardComplaintDocumentResource, self).put()

    @json_view(content_type="application/json", validators=(validate_patch_document_data,), permission="edit_complaint")
    def patch(self):
        """Tender Award Complaint Document Update"""
        if not self.validate_complaint_document("update"):
            return
        return super(TenderAwardComplaintDocumentResource, self).patch()
