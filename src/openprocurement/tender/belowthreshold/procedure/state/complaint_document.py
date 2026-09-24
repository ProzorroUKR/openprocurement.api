from openprocurement.tender.belowthreshold.constants import STATUS4ROLE
from openprocurement.tender.core.procedure.state.complaint_document import (
    ComplaintDocumentState,
)


class BelowThresholdComplaintDocumentState(ComplaintDocumentState):
    allowed_complaint_status_for_role = STATUS4ROLE
