from openprocurement.tender.competitiveordering.constants import STATUS4ROLE
from openprocurement.tender.core.procedure.state.award_complaint_document import (
    AwardComplaintDocumentState,
)


class COAwardComplaintDocumentState(AwardComplaintDocumentState):
    allowed_complaint_status_for_role = STATUS4ROLE
    allowed_tender_statuses = (
        "active.enquiries",
        "active.tendering",
        "active.auction",
        "active.qualification",
        "active.awarded",
    )
