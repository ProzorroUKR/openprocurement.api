from openprocurement.tender.core.procedure.views.cancellation_document import CancellationDocumentResource
from cornice.resource import resource


@resource(
    name="reporting:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType="reporting",
    description="Tender cancellation documents",
)
class ReportingCancellationDocumentResource(CancellationDocumentResource):
    pass


@resource(
    name="negotiation:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType="negotiation",
    description="Tender cancellation documents",
)
class NegotiationCancellationDocumentResource(CancellationDocumentResource):
    pass


@resource(
    name="negotiation.quick:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType="negotiation.quick",
    description="Tender cancellation documents",
)
class NegotiationQuickCancellationDocumentResource(CancellationDocumentResource):
    pass
