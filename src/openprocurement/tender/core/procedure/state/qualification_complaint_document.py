from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.tender.core.procedure.state.complaint_document import (
    ComplaintDocumentState,
)


class QualificationComplaintDocumentState(ComplaintDocumentState):
    allowed_tender_statuses = ("active.pre-qualification", "active.pre-qualification.stand-still")

    def validate_lot_status(self):
        tender = get_tender()
        qualification = self.request.validated["qualification"]
        lot_id = qualification.get("lotID")
        if lot_id and any(lot.get("status") != "active" for lot in tender.get("lots", []) if lot["id"] == lot_id):
            operation = OPERATIONS.get(self.request.method)
            raise_operation_error(self.request, f"Can {operation} document only in active lot status")
