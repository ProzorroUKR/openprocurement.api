from openprocurement.tender.core.procedure.state.complaint_document import (
    ComplaintDocumentState,
)
from openprocurement.tender.open.constants import STATUS4ROLE


class OpenUAComplaintDocumentState(ComplaintDocumentState):
    allowed_complaint_status_for_role = STATUS4ROLE
