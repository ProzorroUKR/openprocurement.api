from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.core.procedure.views.cancellation_document import (
    CancellationDocumentResource as BaseCancellationDocumentResource,
)


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tender cancellation documents",
)
class COCancellationDocumentResource(BaseCancellationDocumentResource):
    pass
