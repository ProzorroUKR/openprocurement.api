from openprocurement.tender.core.procedure.state.award_complaint_document import (
    AwardComplaintDocumentState,
)
from openprocurement.tender.open.constants import STATUS4ROLE


class CFAUAAwardComplaintDocumentState(AwardComplaintDocumentState):
    allowed_complaint_status_for_role = STATUS4ROLE
    allowed_tender_statuses = (
        "active.qualification.stand-still",
        "active.qualification",
    )
    all_documents_should_be_public = True
