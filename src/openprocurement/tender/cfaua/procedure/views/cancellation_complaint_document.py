from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.cancellation_complaint_document import (
    CFAUACancellationComplaintDocumentState,
)
from openprocurement.tender.core.procedure.views.cancellation_complaint_document import (
    CancellationComplaintDocumentResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Cancellation Complaint Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender cancellation complaint documents",
)
class CFAUACancellationComplaintDocumentResource(CancellationComplaintDocumentResource):
    state_class = CFAUACancellationComplaintDocumentState
