from openprocurement.tender.openeu.procedure.views.cancellation_document import EUCancellationDocumentResource
from cornice.resource import resource


@resource(
    name="esco:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType="esco",
    description="Tender ESCO cancellation documents",
)
class ESCOCancellationDocumentResource(EUCancellationDocumentResource):
    pass
