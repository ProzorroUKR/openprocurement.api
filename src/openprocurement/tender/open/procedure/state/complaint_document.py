from openprocurement.tender.core.procedure.state.complaint_document import (
    ComplaintDocumentState,
)
from openprocurement.tender.open.constants import BELOW_THRESHOLD_STATUS4ROLE, REQUEST_FOR_PROPOSAL_STATUS4ROLE


class AboveThresholdComplaintDocumentState(ComplaintDocumentState):
    pass


class AboveThresholdUAComplaintDocumentState(ComplaintDocumentState):
    complaint_document_allowed_tender_statuses = (
        "active.enquiries",
        "active.tendering",
        "active.pre-qualification",
        "active.auction",
        "active.qualification",
        "active.awarded",
    )


class COComplaintDocumentState(ComplaintDocumentState):
    pass


class BelowThresholdComplaintDocumentState(ComplaintDocumentState):
    allowed_complaint_status_for_role = BELOW_THRESHOLD_STATUS4ROLE


class RFPComplaintDocumentState(ComplaintDocumentState):
    allowed_complaint_status_for_role = REQUEST_FOR_PROPOSAL_STATUS4ROLE
