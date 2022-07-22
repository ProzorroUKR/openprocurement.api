from openprocurement.tender.core.procedure.views.cancellation_document import CancellationDocumentResource
from cornice.resource import resource


@resource(
    name="aboveThresholdUA:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender UA cancellation documents",
)
class UACancellationDocumentResource(CancellationDocumentResource):
    pass
