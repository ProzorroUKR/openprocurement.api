from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.complaint_post_document import (
    CFAUAComplaintPostDocumentState,
)
from openprocurement.tender.core.procedure.views.cancellation_complaint_post_document import (
    BaseCancellationComplaintPostDocumentResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Cancellation Complaint Post Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender cancellation complaint post documents",
)
class CFAUACancellationComplaintPostDocumentResource(BaseCancellationComplaintPostDocumentResource):
    state_class = CFAUAComplaintPostDocumentState
