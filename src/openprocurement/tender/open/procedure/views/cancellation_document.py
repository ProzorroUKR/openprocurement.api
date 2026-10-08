from cornice.resource import resource

from openprocurement.tender.core.procedure.state.cancellation_document import CancellationDocumentState
from openprocurement.tender.core.procedure.views.cancellation_document import CancellationDocumentResource
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD,
    ABOVE_THRESHOLD_EU,
    ABOVE_THRESHOLD_UA,
    ABOVE_THRESHOLD_UA_DEFENSE,
    BELOW_THRESHOLD,
    COMPETITIVE_ORDERING,
    OPEN_PROCUREMENT_METHOD_TYPES,
    OPEN_ROUTE_PREFIX,
    REQUEST_FOR_PROPOSAL,
    SIMPLE_DEFENSE,
)
from openprocurement.tender.open.procedure.state.cancellation_document import (
    BelowThresholdCancellationDocumentState,
    RFPCancellationDocumentState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    description="Tender cancellation documents",
    procurementMethodType=OPEN_PROCUREMENT_METHOD_TYPES,
)
class OpenCancellationDocumentResource(CancellationDocumentResource):
    state_classes = {
        ABOVE_THRESHOLD: CancellationDocumentState,
        ABOVE_THRESHOLD_UA: CancellationDocumentState,
        ABOVE_THRESHOLD_EU: CancellationDocumentState,
        ABOVE_THRESHOLD_UA_DEFENSE: CancellationDocumentState,
        SIMPLE_DEFENSE: CancellationDocumentState,
        COMPETITIVE_ORDERING: CancellationDocumentState,
        BELOW_THRESHOLD: BelowThresholdCancellationDocumentState,
        REQUEST_FOR_PROPOSAL: RFPCancellationDocumentState,
    }
