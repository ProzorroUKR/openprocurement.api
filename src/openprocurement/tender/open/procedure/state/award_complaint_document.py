from openprocurement.tender.core.procedure.state.award_complaint_document import (
    AwardComplaintDocumentState,
)
from openprocurement.tender.open.constants import BELOW_THRESHOLD_STATUS4ROLE, REQUEST_FOR_PROPOSAL_STATUS4ROLE


class AboveThresholdAwardComplaintDocumentState(AwardComplaintDocumentState):
    pass


class AboveThresholdUAAwardComplaintDocumentState(AwardComplaintDocumentState):
    pass


class COAwardComplaintDocumentState(AwardComplaintDocumentState):
    pass


class BelowThresholdAwardComplaintDocumentState(AwardComplaintDocumentState):
    allowed_complaint_status_for_role = BELOW_THRESHOLD_STATUS4ROLE
    complaint_document_allowed_tender_statuses = ("active.qualification", "active.awarded")


class RFPAwardComplaintDocumentState(AwardComplaintDocumentState):
    allowed_complaint_status_for_role = REQUEST_FOR_PROPOSAL_STATUS4ROLE
    complaint_document_allowed_tender_statuses = ("active.qualification", "active.awarded")
