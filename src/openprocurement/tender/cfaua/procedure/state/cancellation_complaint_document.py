from openprocurement.tender.core.procedure.state.complaint_document import ComplaintDocumentState


class CFAUACancellationComplaintDocumentState(ComplaintDocumentState):
    all_documents_should_be_public = True
    complaint_document_allowed_tender_statuses = (
        "active.enquiries",
        "active.tendering",
        "active.pre-qualification",
        "active.auction",
        "active.qualification",
        "active.awarded",
    )
