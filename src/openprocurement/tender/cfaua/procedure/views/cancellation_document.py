from openprocurement.tender.core.procedure.views.cancellation_document import CancellationDocumentResource
from cornice.resource import resource


@resource(
    name="closeFrameworkAgreementUA:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender EU cancellation documents",
)
class CFAUACancellationDocumentResource(CancellationDocumentResource):
    pass
