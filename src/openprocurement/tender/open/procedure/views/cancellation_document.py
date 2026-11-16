from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.state.cancellation_document import CancellationDocumentState
from openprocurement.tender.core.procedure.views.cancellation_document import CancellationDocumentResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX, OpenProcurementMethodType
from openprocurement.tender.open.procedure.state.cancellation_document import (
    BelowThresholdCancellationDocumentState,
    RFPCancellationDocumentState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    description="Tender cancellation documents",
    procurementMethodType=OpenProcurementMethodType,
)
class OpenCancellationDocumentResource(CancellationDocumentResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: CancellationDocumentState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: CancellationDocumentState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: CancellationDocumentState,
        ProcurementMethodType.OPEN_TENDERING: CancellationDocumentState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: CancellationDocumentState,
        ProcurementMethodType.SIMPLE_DEFENSE: CancellationDocumentState,
        ProcurementMethodType.COMPETITIVE_ORDERING: CancellationDocumentState,
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdCancellationDocumentState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPCancellationDocumentState,
    }
