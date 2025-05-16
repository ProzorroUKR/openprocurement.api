from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.complaint_appeal_document import (
    CFAUAComplaintAppealDocumentState,
)
from openprocurement.tender.core.procedure.views.cancellation_complaint_appeal_document import (
    BaseCancellationComplaintAppealDocumentResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Cancellation Complaint Appeal Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender cancellation complaint appeal documents",
)
class CFAUACancellationComplaintAppealDocumentResource(BaseCancellationComplaintAppealDocumentResource):
    state_class = CFAUAComplaintAppealDocumentState
