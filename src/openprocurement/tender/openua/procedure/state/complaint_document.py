from openprocurement.tender.core.procedure.state.complaint_document import (
    ComplaintDocumentState,
)


class OpenUAComplaintDocumentState(ComplaintDocumentState):
    complaint_document_allowed_tender_statuses = (
        "active.enquiries",
        "active.tendering",
        "active.pre-qualification",
        "active.auction",
        "active.qualification",
        "active.awarded",
    )
