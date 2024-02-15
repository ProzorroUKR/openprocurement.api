from cornice.resource import resource

from openprocurement.tender.core.procedure.views.cancellation_complaint_post import (
    BaseCancellationComplaintPostResource,
)


@resource(
    name="negotiation:Tender Cancellation Complaint Posts",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType="negotiation",
    description="Tender cancellation complaint posts",
)
class NegotiationCancellationComplaintPostResource(BaseCancellationComplaintPostResource):
    pass


@resource(
    name="negotiation.quick:Tender Cancellation Complaint Posts",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType="negotiation.quick",
    description="Tender cancellation complaint posts",
)
class NegotiationQuickCancellationComplaintPostResource(BaseCancellationComplaintPostResource):
    pass
