from cornice.resource import resource

from openprocurement.tender.core.procedure.views.cancellation_complaint_document import (
    CancellationComplaintDocumentResource,
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
from openprocurement.tender.open.procedure.state.complaint_document import (
    AboveThresholdComplaintDocumentState,
    AboveThresholdUAComplaintDocumentState,
    COComplaintDocumentState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Cancellation Complaint Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents/{document_id}",
    description="Tender cancellation complaint documents",
    procurementMethodType=[
        ABOVE_THRESHOLD,
        ABOVE_THRESHOLD_UA,
        ABOVE_THRESHOLD_EU,
        ABOVE_THRESHOLD_UA_DEFENSE,
        SIMPLE_DEFENSE,
        COMPETITIVE_ORDERING,
    ],
)
class OpenCancellationComplaintDocumentResource(CancellationComplaintDocumentResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdComplaintDocumentState,
        ABOVE_THRESHOLD_UA: AboveThresholdUAComplaintDocumentState,
        ABOVE_THRESHOLD_EU: AboveThresholdUAComplaintDocumentState,
        ABOVE_THRESHOLD_UA_DEFENSE: AboveThresholdUAComplaintDocumentState,
        SIMPLE_DEFENSE: AboveThresholdUAComplaintDocumentState,
        COMPETITIVE_ORDERING: COComplaintDocumentState,
    }
