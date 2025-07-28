from openprocurement.tender.open.procedure.state.complaint_document import (
    OpenComplaintDocumentState,
)


class NegotiationCancellationComplaintDocumentState(OpenComplaintDocumentState):
    allowed_tender_statuses = ("active",)
