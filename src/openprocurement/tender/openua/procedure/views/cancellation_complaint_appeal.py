from cornice.resource import resource

from openprocurement.tender.core.procedure.views.cancellation_complaint_appeal import (
    BaseCancellationComplaintAppealResource,
)
from openprocurement.tender.openua.constants import ABOVE_THRESHOLD_UA


@resource(
    name=f"{ABOVE_THRESHOLD_UA}:Tender Cancellation Complaint Appeals",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=ABOVE_THRESHOLD_UA,
    description="Tender cancellation complaint appeals",
)
class OpenUACancellationComplaintAppealResource(BaseCancellationComplaintAppealResource):
    pass
