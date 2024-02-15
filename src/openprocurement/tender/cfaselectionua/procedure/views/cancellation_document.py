from cornice.resource import resource

from openprocurement.tender.core.procedure.views.cancellation_document import (
    CancellationDocumentResource,
)


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Cancellation Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender cancellation documents",
)
class CFASelectionCancellationDocument(CancellationDocumentResource):
    pass
