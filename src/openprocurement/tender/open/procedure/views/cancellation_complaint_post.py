from openprocurement.tender.core.procedure.views.cancellation_complaint_post import (
    BaseCancellationComplaintPostResource,
)
from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from cornice.resource import resource


@resource(
    name=f"{ABOVE_THRESHOLD}:Tender Cancellation Complaint Posts",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    description="Tender cancellation complaint posts",
)
class OpenCancellationComplaintPostResource(BaseCancellationComplaintPostResource):
    pass
