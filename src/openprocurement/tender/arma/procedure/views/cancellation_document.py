from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.cancellation_document import (
    CancellationDocumentResource as BaseCancellationDocumentResource,
)


@resource(
    name="complexAsset.arma:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender cancellation documents",
)
class CancellationDocumentResource(BaseCancellationDocumentResource):
    pass
