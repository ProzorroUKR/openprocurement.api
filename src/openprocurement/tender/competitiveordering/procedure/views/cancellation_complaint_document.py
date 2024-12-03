from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.competitiveordering.procedure.state.complaint_document import (
    OpenComplaintDocumentState,
)
from openprocurement.tender.core.procedure.views.cancellation_complaint_document import (
    CancellationComplaintDocumentResource,
)


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Cancellation Complaint Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tender cancellation complaint documents",
)
class OpenCancellationComplaintDocumentResource(CancellationComplaintDocumentResource):
    state_class = OpenComplaintDocumentState
