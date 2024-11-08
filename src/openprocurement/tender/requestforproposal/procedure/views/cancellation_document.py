from cornice.resource import resource

from openprocurement.tender.core.procedure.views.cancellation_document import (
    CancellationDocumentResource,
)
from openprocurement.tender.requestforproposal.procedure.state.cancellation_document import (
    BTCancellationDocumentState,
)


@resource(
    name="requestForProposal:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType="requestForProposal",
    description="Tender cancellation documents",
)
class BTCancellationDocument(CancellationDocumentResource):
    state_class = BTCancellationDocumentState
