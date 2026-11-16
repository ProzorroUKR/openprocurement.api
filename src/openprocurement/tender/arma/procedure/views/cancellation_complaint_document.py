from cornice.resource import resource

from openprocurement.tender.arma.constants import ARMA_ROUTE_PREFIX, ARMAProcurementMethodType
from openprocurement.tender.core.procedure.views.cancellation_complaint_document import (
    CancellationComplaintDocumentResource as BaseCancellationComplaintDocumentResource,
)
from openprocurement.tender.open.procedure.state.complaint_document import (
    AboveThresholdUAComplaintDocumentState,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Cancellation Complaint Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=ARMAProcurementMethodType,
    description="Tender cancellation complaint documents",
)
class CancellationComplaintDocumentResource(BaseCancellationComplaintDocumentResource):
    state_class = AboveThresholdUAComplaintDocumentState
