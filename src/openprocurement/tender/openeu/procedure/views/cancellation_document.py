from openprocurement.tender.core.procedure.views.cancellation_document import CancellationDocumentResource
from cornice.resource import resource


@resource(
    name="aboveThresholdEU:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender EU cancellation documents",
)
class EUCancellationDocumentResource(CancellationDocumentResource):
    pass
