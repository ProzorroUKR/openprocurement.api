from cornice.resource import resource

from openprocurement.tender.core.procedure.views.cancellation_complaint_appeal_document import (
    BaseCancellationComplaintAppealDocumentResource,
)
from openprocurement.tender.openua.constants import ABOVE_THRESHOLD_UA


@resource(
    name=f"{ABOVE_THRESHOLD_UA}:Tender Cancellation Complaint Appeal Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=ABOVE_THRESHOLD_UA,
    description="Tender cancellation complaint appeal documents",
)
class OpenUACancellationComplaintAppealDocumentResource(BaseCancellationComplaintAppealDocumentResource):
    pass
