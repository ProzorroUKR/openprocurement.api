from cornice.resource import resource

from openprocurement.tender.belowthreshold.procedure.state.cancellation_document import (
    BTCancellationDocumentState,
)
from openprocurement.tender.core.procedure.views.cancellation_document import (
    CancellationDocumentResource,
)


@resource(
    name="belowThreshold:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType="belowThreshold",
    description="Tender cancellation documents",
)
class BTCancellationDocument(CancellationDocumentResource):
    state_class = BTCancellationDocumentState
