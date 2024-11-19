from cornice.resource import resource

from openprocurement.tender.core.procedure.views.cancellation_document import (
    CancellationDocumentResource,
)
from openprocurement.tender.pricequotation.constants import PQ


@resource(
    name=f"{PQ}:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType=PQ,
    description="Tender cancellation documents",
)
class PQCancellationDocumentResource(CancellationDocumentResource):
    pass
