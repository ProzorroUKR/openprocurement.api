from cornice.resource import resource

from openprocurement.tender.arma.constants import ARMA_PROCUREMENT_METHOD_TYPES, ARMA_ROUTE_PREFIX
from openprocurement.tender.core.procedure.views.cancellation_document import (
    CancellationDocumentResource as BaseCancellationDocumentResource,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    description="Tender cancellation documents",
)
class CancellationDocumentResource(BaseCancellationDocumentResource):
    pass
