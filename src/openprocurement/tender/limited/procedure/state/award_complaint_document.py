from openprocurement.tender.core.procedure.state.award_complaint_document import (
    AwardComplaintDocumentState,
)


class NegotiationAwardComplaintDocumentState(AwardComplaintDocumentState):
    complaint_document_allowed_tender_statuses = ("active",)
