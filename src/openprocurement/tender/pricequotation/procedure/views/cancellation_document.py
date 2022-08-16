from openprocurement.tender.core.procedure.views.cancellation_document import CancellationDocumentResource
from openprocurement.tender.pricequotation.constants import PMT
from cornice.resource import resource


@resource(
    name="{}:Tender Cancellation Documents".format(PMT),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType=PMT,
    description="Tender cancellation documents",
)
class PQCancellationDocumentResource(CancellationDocumentResource):
    pass
