from cornice.resource import resource

from openprocurement.tender.core.procedure.views.cancellation_complaint_document import (
    CancellationComplaintDocumentResource,
)
from openprocurement.tender.limited.procedure.state.cancellation_complaint_documents import (
    NegotiationCancellationComplaintDocumentState,
)


@resource(
    name="negotiation:Tender Cancellation Complaint Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="negotiation",
    description="Tender negotiation cancellation complaint documents",
)
class NegotiationCancellationComplaintDocumentResource(CancellationComplaintDocumentResource):
    state_class = NegotiationCancellationComplaintDocumentState


@resource(
    name="negotiation.quick:Tender Cancellation Complaint Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="negotiation.quick",
    description="Tender negotiation.quick cancellation complaint documents",
)
class NegotiationQuickCancellationComplaintDocumentResource(CancellationComplaintDocumentResource):
    state_class = NegotiationCancellationComplaintDocumentState
