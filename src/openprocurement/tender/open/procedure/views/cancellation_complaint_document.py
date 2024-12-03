from cornice.resource import resource

from openprocurement.tender.core.procedure.views.cancellation_complaint_document import (
    CancellationComplaintDocumentResource,
)
from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.open.procedure.state.complaint_document import (
    OpenComplaintDocumentState,
)


@resource(
    name=f"{ABOVE_THRESHOLD}:Tender Cancellation Complaint Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    description="Tender cancellation complaint documents",
)
class OpenCancellationComplaintDocumentResource(CancellationComplaintDocumentResource):
    state_class = OpenComplaintDocumentState
