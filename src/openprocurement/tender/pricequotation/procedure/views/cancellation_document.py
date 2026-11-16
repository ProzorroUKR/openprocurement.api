from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.cancellation_document import (
    CancellationDocumentResource,
)


@resource(
    name=f"{ProcurementMethodType.PRICE_QUOTATION}:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.PRICE_QUOTATION,
    description="Tender cancellation documents",
)
class PQCancellationDocumentResource(CancellationDocumentResource):
    pass
