from cornice.resource import resource

from openprocurement.tender.arma.constants import ARMA_PROCUREMENT_METHOD_TYPES, ARMA_ROUTE_PREFIX
from openprocurement.tender.core.procedure.views.cancellation_complaint_appeal import (
    BaseCancellationComplaintAppealResource,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Cancellation Complaint Appeals",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    description="Tender cancellation complaint appeals",
)
class CancellationComplaintAppealResource(BaseCancellationComplaintAppealResource):
    pass
