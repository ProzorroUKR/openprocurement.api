from openprocurement.tender.openua.procedure.views.cancellation_document import UACancellationDocumentResource
from cornice.resource import resource


@resource(
    name="aboveThresholdUA.defense:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender UA.defense cancellation documents",
)
class UADefenseCancellationDocumentResource(UACancellationDocumentResource):
    pass
