from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.cancellation_complaint_document import (
    CancellationComplaintDocumentResource,
)
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX
from openprocurement.tender.open.procedure.state.complaint_document import (
    AboveThresholdComplaintDocumentState,
    AboveThresholdUAComplaintDocumentState,
    COComplaintDocumentState,
    OpenTenderingCancellationComplaintDocumentState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Cancellation Complaint Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/documents/{document_id}",
    description="Tender cancellation complaint documents",
    procurementMethodType=[
        ProcurementMethodType.ABOVE_THRESHOLD,
        ProcurementMethodType.ABOVE_THRESHOLD_UA,
        ProcurementMethodType.ABOVE_THRESHOLD_EU,
        ProcurementMethodType.OPEN_TENDERING,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE,
        ProcurementMethodType.SIMPLE_DEFENSE,
        ProcurementMethodType.COMPETITIVE_ORDERING,
    ],
)
class OpenCancellationComplaintDocumentResource(CancellationComplaintDocumentResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdComplaintDocumentState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUAComplaintDocumentState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdUAComplaintDocumentState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingCancellationComplaintDocumentState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: AboveThresholdUAComplaintDocumentState,
        ProcurementMethodType.SIMPLE_DEFENSE: AboveThresholdUAComplaintDocumentState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COComplaintDocumentState,
    }
