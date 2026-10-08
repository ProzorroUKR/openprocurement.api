from openprocurement.tender.core.procedure.state.award_complaint_document import (
    AwardComplaintDocumentState,
)


class CFAUAAwardComplaintDocumentState(AwardComplaintDocumentState):
    complaint_document_allowed_tender_statuses = (
        "active.qualification.stand-still",
        "active.qualification",
    )
    all_documents_should_be_public = True
