from cornice.resource import resource

from openprocurement.tender.core.procedure.views.cancellation_complaint_appeal import (
    BaseCancellationComplaintAppealResource,
)


@resource(
    name="aboveThresholdEU:Tender Cancellation Complaint Appeals",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender cancellation complaint appeals",
)
class OpenEUCancellationComplaintAppealResource(BaseCancellationComplaintAppealResource):
    pass
