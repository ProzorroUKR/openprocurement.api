from cornice.resource import resource

from openprocurement.tender.core.procedure.views.cancellation_complaint_post import (
    BaseCancellationComplaintPostResource,
)
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD,
    ABOVE_THRESHOLD_EU,
    ABOVE_THRESHOLD_UA,
    ABOVE_THRESHOLD_UA_DEFENSE,
    COMPETITIVE_ORDERING,
    OPEN_ROUTE_PREFIX,
    SIMPLE_DEFENSE,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Cancellation Complaint Posts",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}",
    description="Tender cancellation complaint posts",
    procurementMethodType=[
        ABOVE_THRESHOLD,
        ABOVE_THRESHOLD_UA,
        ABOVE_THRESHOLD_EU,
        ABOVE_THRESHOLD_UA_DEFENSE,
        SIMPLE_DEFENSE,
        COMPETITIVE_ORDERING,
    ],
)
class OpenBaseCancellationComplaintPostResource(BaseCancellationComplaintPostResource):
    pass
