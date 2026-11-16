from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.cancellation_document import (
    CancellationDocumentResource,
)


@resource(
    name="reporting:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.REPORTING,
    description="Tender cancellation documents",
)
class ReportingCancellationDocumentResource(CancellationDocumentResource):
    pass


@resource(
    name="negotiation:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.NEGOTIATION,
    description="Tender cancellation documents",
)
class NegotiationCancellationDocumentResource(CancellationDocumentResource):
    pass


@resource(
    name="negotiation.quick:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.NEGOTIATION_QUICK,
    description="Tender cancellation documents",
)
class NegotiationQuickCancellationDocumentResource(CancellationDocumentResource):
    pass
