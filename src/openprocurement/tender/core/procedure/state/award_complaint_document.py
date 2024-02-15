from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.tender.core.procedure.context import get_award
from openprocurement.tender.core.procedure.state.complaint_document import (
    ComplaintDocumentState,
)


class AwardComplaintDocumentState(ComplaintDocumentState):
    def validate_lot_status(self):
        tender = get_tender()
        award = get_award()
        lot_id = award.get("lotID")
        if lot_id and any(
            lot.get("status") != "active" for lot in tender.get("lots", []) if lot["id"] == award.get("lotID")
        ):
            operation = OPERATIONS.get(self.request.method)
            raise_operation_error(self.request, f"Can {operation} document only in active lot status")
