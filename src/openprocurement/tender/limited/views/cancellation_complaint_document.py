from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.cancellation_complaint_document import \
    BaseTenderComplaintCancellationDocumentResource



@optendersresource(
    name="negotiation:Tender Cancellation Complaint Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="negotiation",
    description="Tender negotiation cancellation complaint documents",
)
class NegotiationCancellationComplaintDocument(BaseTenderComplaintCancellationDocumentResource):
    pass


@optendersresource(
    name="negotiation.quick:Tender Cancellation Complaint Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="negotiation.quick",
    description="Tender negotiation.quick cancellation complaint documents",
)
class NegotiationQuickCancellationComplaintDocument(BaseTenderComplaintCancellationDocumentResource):
    pass
