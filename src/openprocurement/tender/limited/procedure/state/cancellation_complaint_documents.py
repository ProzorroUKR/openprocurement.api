from openprocurement.tender.core.procedure.state.complaint_document import ComplaintDocumentState


class NegotiationCancellationComplaintDocumentState(ComplaintDocumentState):
    complaint_document_allowed_tender_statuses = ("active",)
