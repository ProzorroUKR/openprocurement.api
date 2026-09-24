from openprocurement.tender.core.procedure.state.complaint_document import (
    ComplaintDocumentState,
)
from openprocurement.tender.requestforproposal.constants import STATUS4ROLE


class RFPComplaintDocumentState(ComplaintDocumentState):
    allowed_complaint_status_for_role = STATUS4ROLE
