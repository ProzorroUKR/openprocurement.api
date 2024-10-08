from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.tender.belowthreshold.constants import STATUS4ROLE
from openprocurement.tender.core.procedure.context import get_award
from openprocurement.tender.core.procedure.state.complaint_document import (
    ComplaintDocumentState,
)


class BTAwardComplaintDocumentState(ComplaintDocumentState):
    def validate_document_post(self, data):
        tender = get_tender()
        award = get_award()
        if document := self.request.validated.get("document"):  # POST new version via PUT method
            self.validate_document_author(document)
        self.validate_tender_status()
        self.validate_active_lot_status(tender, award)
        self.validate_complaint_status()

    def validate_document_patch(self, before, after):
        tender = get_tender()
        award = get_award()
        self.validate_document_author(before)
        self.validate_tender_status()
        self.validate_active_lot_status(tender, award)
        self.validate_complaint_status()

    def validate_complaint_status(self):
        complaint = self.request.validated["complaint"]
        status = complaint.get("status")
        if status not in STATUS4ROLE.get(self.request.authenticated_role, []):
            operation = OPERATIONS.get(self.request.method)
            raise_operation_error(
                self.request,
                f"Can't {operation} document in current ({status}) complaint status",
            )

    def validate_tender_status(self):
        tender = get_tender()
        status = tender["status"]
        if status not in (
            "active.qualification",
            "active.awarded",
        ):
            operation = OPERATIONS.get(self.request.method)
            raise_operation_error(
                self.request,
                f"Can't {operation} document in current ({status}) tender status",
            )

    def validate_document_author(self, document):
        if self.request.authenticated_role != document["author"]:
            raise_operation_error(
                self.request,
                "Can update document only author",
                location="url",
                name="role",
            )

    def validate_active_lot_status(self, tender, award):
        if lot_id := award.get("lotID"):
            if any(i.get("status") != "active" for i in tender.get("lots", "") if i["id"] == lot_id):
                operation = OPERATIONS.get(self.request.method)
                raise_operation_error(self.request, f"Can {operation} document only in active lot status")
