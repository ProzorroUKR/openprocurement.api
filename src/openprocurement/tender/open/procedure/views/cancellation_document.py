from openprocurement.tender.core.procedure.views.cancellation_document import CancellationDocumentResource
from cornice.resource import resource

from openprocurement.tender.open.constants import ABOVE_THRESHOLD


@resource(
    name=f"{ABOVE_THRESHOLD}:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    description="Tender cancellation documents",
)
class CancellationDocumentResource(CancellationDocumentResource):
    pass
