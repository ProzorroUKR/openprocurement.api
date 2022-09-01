from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.cancellation_complaint_document import \
    BaseTenderComplaintCancellationDocumentResource
from openprocurement.tender.open.constants import ABOVE_THRESHOLD


@optendersresource(
    name=f"{ABOVE_THRESHOLD}:Tender Cancellation Complaint Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    description="Tender cancellation complaint documents",
)
class TenderCancellationComplaintDocument(BaseTenderComplaintCancellationDocumentResource):
    pass
