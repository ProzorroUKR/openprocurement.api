from cornice.resource import resource

from openprocurement.tender.core.procedure.views.cancellation_complaint_appeal import (
    BaseCancellationComplaintAppealResource,
)


@resource(
    name="negotiation:Tender Cancellation Complaint Appeals",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType="negotiation",
    description="Tender cancellation complaint appeals",
)
class NegotiationCancellationComplaintAppealResource(BaseCancellationComplaintAppealResource):
    pass


@resource(
    name="negotiation.quick:Tender Cancellation Complaint Appeals",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType="negotiation.quick",
    description="Tender cancellation complaint appeals",
)
class NegotiationQuickCancellationComplaintAppealResource(BaseCancellationComplaintAppealResource):
    pass
