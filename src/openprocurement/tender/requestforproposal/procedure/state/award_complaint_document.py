from openprocurement.tender.core.procedure.state.award_complaint_document import (
    AwardComplaintDocumentState,
)
from openprocurement.tender.requestforproposal.constants import STATUS4ROLE


class RFPAwardComplaintDocumentState(AwardComplaintDocumentState):
    allowed_complaint_status_for_role = STATUS4ROLE
    complaint_document_allowed_tender_statuses = ("active.qualification", "active.awarded")
