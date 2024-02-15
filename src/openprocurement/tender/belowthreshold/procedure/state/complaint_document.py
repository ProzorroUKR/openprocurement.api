from openprocurement.tender.belowthreshold.constants import STATUS4ROLE
from openprocurement.tender.core.procedure.state.complaint_document import (
    ComplaintDocumentState,
)


class BTComplaintDocumentState(ComplaintDocumentState):
    allowed_complaint_status_for_role = STATUS4ROLE
    allowed_tender_statuses = (
        "active.enquiries",
        "active.tendering",
        "active.auction",
        "active.qualification",
        "active.awarded",
    )
