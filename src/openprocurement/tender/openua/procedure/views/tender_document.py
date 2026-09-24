from cornice.resource import resource

from openprocurement.tender.core.procedure.views.tender_document import (
    TenderDocumentResource,
)
from openprocurement.tender.openua.procedure.state.tender_document import (
    OpenUATenderDocumentState,
)


@resource(
    name="aboveThresholdUA:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender UA related binary files (PDFs, etc.)",
)
class UATenderDocumentResource(TenderDocumentResource):
    state_class = OpenUATenderDocumentState
