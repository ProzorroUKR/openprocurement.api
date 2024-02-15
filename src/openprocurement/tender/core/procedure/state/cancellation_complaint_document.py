from openprocurement.tender.core.procedure.state.complaint_document import ComplaintDocumentState
from openprocurement.tender.core.procedure.context import get_cancellation
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS


class CancellationComplaintDocumentState(ComplaintDocumentState):
    def validate_lot_status(self):
        tender = get_tender()
        cancellation = get_cancellation()
        lot_id = cancellation.get("relatedLot")
        if lot_id and any(lot.get("status") != "active" for lot in tender.get("lots", []) if lot["id"] == lot_id):
            operation = OPERATIONS.get(self.request.method)
            raise_operation_error(self.request, f"Can {operation} document only in active lot status")
