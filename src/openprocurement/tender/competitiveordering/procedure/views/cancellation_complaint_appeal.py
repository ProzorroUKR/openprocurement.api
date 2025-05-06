from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.core.procedure.views.cancellation_complaint_appeal import (
    BaseCancellationComplaintAppealResource,
)


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Cancellation Complaint Appeals",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tender cancellation complaint appeals",
)
class COCancellationComplaintAppealResource(BaseCancellationComplaintAppealResource):
    pass
