from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.cancellation_document import (
    CFAUACancellationDocumentState,
)
from openprocurement.tender.core.procedure.views.cancellation_document import (
    CancellationDocumentResource,
)


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender cancellation documents",
)
class CFASelectionCancellationDocument(CancellationDocumentResource):
    state_class = CFAUACancellationDocumentState
