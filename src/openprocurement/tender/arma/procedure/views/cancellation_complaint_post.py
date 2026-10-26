from cornice.resource import resource

from openprocurement.tender.arma.constants import ARMA_PROCUREMENT_METHOD_TYPES, ARMA_ROUTE_PREFIX
from openprocurement.tender.core.procedure.views.cancellation_complaint_post import (
    BaseCancellationComplaintPostResource,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Cancellation Complaint Posts",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    description="Tender cancellation complaint posts",
)
class CancellationComplaintPostResource(BaseCancellationComplaintPostResource):
    pass
