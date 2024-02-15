from cornice.resource import resource

from openprocurement.tender.core.procedure.views.cancellation_complaint_document import (
    CancellationComplaintDocumentResource,
)
from openprocurement.tender.openua.procedure.state.complaint_document import (
    OpenUAComplaintDocumentState,
)


@resource(
    name="aboveThresholdUA:Tender Cancellation Complaint Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender cancellation complaint documents",
)
class OpenUACancellationComplaintDocumentResource(CancellationComplaintDocumentResource):
    state_class = OpenUAComplaintDocumentState
